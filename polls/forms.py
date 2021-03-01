from django import forms

from .models import Poll, PollUser, form_vote_choices, TopicVote, PollTopic

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Row, Div, Field, Button


class CreatePollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['name']

    def save(self, commit=True):
        """
        Overriding the save function to create a PollUser record in the database for the AnonUser for ease of use
        and saving the PollUser / Poll id's in the session
        :param commit:
        :return: newly created Poll instance
        """
        poll = super(CreatePollForm, self).save(commit=False)
        if 'user_id' in self.request.session:
            poll_user = PollUser.objects.get(id=self.request.session['user_id'])
            poll.created_by = poll_user
        else:
            poll_user = PollUser(
                name='Scrum Master'
            )
            poll_user.save()
            poll.created_by = poll_user
        poll.save()
        return poll

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(CreatePollForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['name'].label = 'Poll name'
        self.fields['name'].help_text = 'Example: Sprint XX planning session'
        self.helper.layout = Layout(
            Row(
                Div(Field(
                    'name'
                ),
                    css_class="col-md-8"
                ),
                css_class='mt-5'
            ),
            Row(
                Div(ButtonHolder(
                    Submit('submit', 'Create poll', css_class='btn btn-block button-success')
                ), css_class="col-md-2 text-center mt-3")
            ),
        )


class JoinAPoll(forms.Form):
    poll_id = forms.UUIDField(label='Session ID')
    name = forms.CharField(max_length=50, label='Your name')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(JoinAPoll, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Div(Field(
                    'poll_id'
                ),
                    css_class="col-md-5"
                ),
                Div(Field(
                    'name'
                ),
                    css_class="offset-md-2 col-md-5"
                ),
                css_class='mt-1'
            ),
            Row(
                Div(ButtonHolder(
                    Submit('submit', 'Join session', css_class='btn btn-block button-success')
                ), css_class="col-md-2 offset-md-5 text-center mt-3")
            ),
        )


class VotingForm(forms.Form):
    vote = forms.ChoiceField(choices=form_vote_choices)

    def __init__(self, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Div(Field(
                    'vote'
                ),
                    css_class="col-md-12"
                ),
                css_class='mt-2'
            ),
            Row(
                Div(ButtonHolder(
                    Button('submit', 'Submit vote', css_class='btn-block btn-primary', css_id='submit-vote-btn')
                ), css_class="col-md-2 offset-md-5 text-center mt-3 mb-3")
            ),
        )

    def save_vote(self, poll_user_id, poll_topic_id):
        topic_vote = TopicVote.objects.filter(
            poll_user_id=poll_user_id,
            poll_topic_id=poll_topic_id
        ).first()
        if topic_vote:
            topic_vote.vote = self.cleaned_data['vote']
        else:
            topic_vote = TopicVote(
                poll_topic_id=poll_topic_id,
                poll_user_id=poll_user_id,
                vote=self.cleaned_data['vote']
            )
        topic_vote.save()
        return topic_vote


class CreatePollTopicForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}))

    class Meta:
        model = PollTopic
        fields = ['title', 'description']

    def save(self, poll_id, commit=True):
        """
        Overriding the save function to create a PollTopic record
        :param commit:
        :param poll_id: UUID representing Poll ID
        :return: newly created PollTopic instance
        """
        poll_topic = super(CreatePollTopicForm, self).save(commit=False)
        poll_topic.poll_id = poll_id
        poll_topic.save()
        return poll_topic

    def __init__(self, *args, **kwargs):
        super(CreatePollTopicForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['title'].label = 'Topic title'
        self.fields['title'].help_text = 'Example: Story #123 - New User Form'
        self.fields['description'].label = 'Topic Description'
        self.fields['title'].help_text = 'Details about the topic'
        self.helper.layout = Layout(
            Row(
                Div(Field(
                    'title'
                ),
                    css_class="col-md-6"
                ),
                Div(Field(
                    'description'
                ),
                    css_class="col-md-6"
                ),
                css_class='mt-3'
            ),
            Row(
                Div(ButtonHolder(
                    Button('submit', 'Create topic', css_class='btn-block btn-primary', css_id='submit-topic-btn')
                ), css_class="col-md-2 text-center mt-3")
            ),
        )

