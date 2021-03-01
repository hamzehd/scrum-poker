from django.contrib import admin
from .models import *

admin.site.register(Poll)
admin.site.register(PollTopic)
admin.site.register(TopicVote)
admin.site.register(Profile)
admin.site.register(PollUser)
