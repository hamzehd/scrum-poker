from django.urls import path

from .views import *

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('create/', CreatePollView.as_view(), name='create_poll'),
    path('poll/<uuid:poll_id>/', poll_detail, name='poll_detail'),
    path('join/', JoinAPollView.as_view(), name='join_poll'),
    path('results/<uuid:poll_id>/', fetch_voting_results, name='fetch_voting_results'),
    path('submit_vote/<int:topic_id>/', submit_vote, name='submit_vote'),
    path('create-topic/<uuid:poll_id>/', start_topic, name='create_topic'),
    path('fetch-poll-members/<uuid:poll_id>/', fetch_poll_members, name='fetch_poll_members'),
    path('fetch-current-topic/<uuid:poll_id>/', fetch_current_topic, name='fetch_current_topic'),
    path('submit-vote/<uuid:poll_id>/', submit_vote, name='submit_vote'),
    path('end-topic-vote/<uuid:poll_id>/', end_topic_voting, name='end_topic_voting'),
]
