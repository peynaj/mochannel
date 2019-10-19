from django.urls import path
from .views import Whoami, CreateUserView, ListUserView, FollowUserView, ListUserPosts, ListUserChannelsView, \
    ListUserLikedPostsView, ListUserBookmarkedPostsView

urlpatterns = [
    path('', ListUserView.as_view(), name='user_list'),
    path('whoami/', Whoami.as_view(), name='whoami'),
    path('register/', CreateUserView.as_view(), name='user_register'),
    path('channels/<int:target_user_id>/', ListUserChannelsView.as_view(), name='user_channels'),
    path('follow/<int:target_user_id>/', FollowUserView.as_view(), name='user_following'),
    path('posts/<int:target_user_id>/', ListUserPosts.as_view(), name='user_posts'),
    path('my_liked/', ListUserLikedPostsView.as_view(), name='my_liked'),
    path('my_bookmarked/', ListUserBookmarkedPostsView.as_view(), name='my_bookmarked'),
]
