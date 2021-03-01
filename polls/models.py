import uuid
from copy import deepcopy

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


vote_choices = [0, 1, 2, 3, 5, 8, 13]

vote_choices_dict = {str(i): i for i in vote_choices}

votes_choices_counts = {str(i): 0 for i in vote_choices}

form_vote_choices = [(str(i), i) for i in vote_choices]


class PollUser(models.Model):
    """
        Just a model to keep track of poll members
    """
    name = models.CharField(max_length=40, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'ID: {self.pk} - {self.name}'


class Poll(models.Model):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    ENDED = 'ended'
    POLL_STATUS = [
        (CREATED, 'Created'),
        (IN_PROGRESS, 'In progress'),
        (ENDED, 'ended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.CharField(choices=POLL_STATUS, default=CREATED, max_length=20)
    members = models.ManyToManyField(PollUser)
    created_by = models.ForeignKey(PollUser, on_delete=models.CASCADE, related_name='poll_creator')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name

    def get_topics(self):
        return PollTopic.objects.filter(
            poll_id=self.id
        ).all()

    def get_active_topic(self):
        active_topic = PollTopic.objects.filter(
            poll_id=self.id,
            is_active=True
        ).first()
        return active_topic

    def poll_started(self):
        self.status = self.IN_PROGRESS
        self.save()


class PollTopic(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return self.title

    def get_votes(self):
        votes = TopicVote.objects.filter(
            poll_topic_id=self.pk
        ).all()
        return votes

    def get_current_votes_count(self):
        votes = self.get_votes()
        current_votes_count = deepcopy(votes_choices_counts)
        for vote in votes:
            current_votes_count[str(vote.vote)] += 1
        return current_votes_count

    def deactivate_poll(self):
        self.is_active = False
        self.save()


class TopicVote(models.Model):
    poll_topic = models.ForeignKey(PollTopic, on_delete=models.CASCADE)
    vote = models.IntegerField()
    poll_user = models.ForeignKey(PollUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'{self.poll_topic.title} - {self.poll_user.name}'


class Profile(models.Model):
    """
    Not Used, built just incase, replaced by PollUser
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
