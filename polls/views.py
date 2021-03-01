from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView


from .forms import CreatePollForm, JoinAPoll, VotingForm, CreatePollTopicForm
from .models import Poll, PollUser, PollTopic


class HomepageView(TemplateView):
    """
        Landing Page View
    """
    template_name = 'index.html'


class CreatePollView(FormView):
    form_class = CreatePollForm
    template_name = 'poll/create-poll.html'

    def get_form_kwargs(self):
        """
        Overriding get_form_kwargs to pass the request to the form.
        :return: kwargs updated with the request
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Overriding form_valid to trigger form.save() and adding user_id/poll_id to the session
        :return: super().form_valid()
        """
        poll = form.save()
        self.request.session['user_id'] = str(poll.created_by.pk)
        self.request.session['poll_id'] = str(poll.id)
        return super().form_valid(form)

    def get_success_url(self):
        poll_id = self.request.session['poll_id']
        return reverse('poll_detail', kwargs={'poll_id': poll_id})


def poll_detail(request, poll_id):
    """
    Detail view for the poll, created as a function view to be able to render the page depending on the user
    :param request:
    :param poll_id: UUID representing Poll ID
    :return: rendered template depending on the user type
    """
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        current_user = PollUser.objects.get(id=user_id)
    else:
        # If there is no user_id in the session, redirect back to join_poll page
        response = redirect('join_poll')
        response['Location'] += f'?poll_id={poll_id}'
        return response
    poll = Poll.objects.get(id=poll_id)
    context = {
        'poll': poll,
        'current_user': current_user,
        'team_members': poll.members.all(),
        'current_topic': poll.get_active_topic(),
        'topics': poll.get_topics()
    }
    if poll.created_by == current_user:
        context['poll_form'] = CreatePollTopicForm()
        return render(request, 'poll/scrum-master-view.html', context)
    else:
        context['voting_form'] = VotingForm()
        return render(request, 'poll/developer-view.html', context)


class JoinAPollView(FormView):
    form_class = JoinAPoll
    template_name = 'poll/join-poll.html'

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        if self.request.GET.get('poll_id'):
            initial['poll_id'] = self.request.GET.get('poll_id')

        return initial

    def get_form_kwargs(self):
        """
        Overriding get_form_kwargs to pass the request to the form.
        :return: kwargs updated with the request
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Overriding form_valid to create a PollUser and adding it to the Poll members
        :return: super().form_valid()
        """
        self.form = form
        if 'user_id' in self.request.session:
            poll_user = PollUser.objects.get(id=self.request.session['user_id'])
            poll_user.name = form.cleaned_data['name']
        else:

            poll_user = PollUser(
                name=form.cleaned_data['name']
            )
        poll_user.save()
        self.request.session['user_id'] = str(poll_user.pk)
        if 'poll_id' in self.request.session and self.request.session['poll_id'] == form.cleaned_data['poll_id']:
            return super().form_valid(form)
        poll = Poll.objects.get(id=form.cleaned_data['poll_id'])
        poll.members.add(poll_user)
        poll.save()
        self.request.session['poll_id'] = str(poll.id)
        return super().form_valid(form)

    def get_success_url(self):
        poll_id = self.form.cleaned_data['poll_id']
        return reverse('poll_detail', kwargs={'poll_id': poll_id})


def fetch_voting_results(request, poll_id):
    """
        View to fetch updated vote results
        :param request:
        :param poll_id: UUID representing Poll ID
        :return: rendered poll-results template
    """
    poll_topics = PollTopic.objects.filter(
        poll_id=poll_id
    ).all()
    return render(request, 'poll/poll-results.html', {'topics': poll_topics})


def fetch_poll_members(request, poll_id):
    """
        View to fetch updated members of the team
        :param request:
        :param poll_id: UUID representing Poll ID
        :return: rendered poll-results template
    """
    poll = Poll.objects.get(id=poll_id)
    return render(request, 'poll/poll-members.html', {'team_members': poll.members.all()})


def fetch_current_topic(request, poll_id):
    """
        View to fetch current topic
        :param request:
        :param poll_id: UUID representing Poll ID
        :return: rendered poll-results template
    """
    poll_topic = PollTopic.objects.filter(
        poll_id=poll_id,
        is_active=True
    ).first()
    if poll_topic.poll.status == Poll.CREATED:
        # Update poll status
        poll_topic.poll.poll_started()
    return render(request, 'poll/poll-topic.html', {'current_topic': poll_topic})


def submit_vote(request, poll_id):
    """
        View to submit vote on current topic
        :param request:
        :param poll_id: UUID representing Poll ID
        :return: dict with message str
    """
    data = {'message': 'Vote received'}
    form = VotingForm(data=request.POST)
    if form.is_valid():
        poll_topic = PollTopic.objects.filter(
            poll_id=poll_id,
            is_active=True
        ).first()
        if poll_topic.poll.status == Poll.CREATED:
            # Update poll status
            poll_topic.poll.poll_started()
        form.save_vote(request.session['user_id'], poll_topic.id)
        data['message'] = 'Vote successful'
    return JsonResponse(data)


def end_topic_voting(request, poll_id):
    poll_topic = PollTopic.objects.filter(
        poll_id=poll_id,
        is_active=True
    ).first()
    poll_topic.deactivate_poll()
    data = {'message': 'Session ended'}
    return JsonResponse(data)


def start_topic(request, poll_id):
    """
        View to submit CreatePollTopicForm
        :param request:
        :param poll_id: UUID representing Poll ID
        :return: dict with message str
    """
    data = {'message': 'Session ended'}
    form = CreatePollTopicForm(data=request.POST)
    if form.is_valid():
        form.save(poll_id)
        data['message'] = 'Topic created'
    return JsonResponse(data)

