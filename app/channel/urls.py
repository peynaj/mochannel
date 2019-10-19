from django.urls import path
from .views import CreateChannelView, ListChannelView, FollowChannelView, ListChannelPosts

urlpatterns = [
    path('', ListChannelView.as_view(), name='channel_list'),
    path('new/', CreateChannelView.as_view(), name='channel_create'),
    path('follow/<int:target_channel_id>/', FollowChannelView.as_view(), name='channel_follow'),
    path('posts/<int:target_channel_id>/', ListChannelPosts.as_view(), name='channel_posts'),
]
