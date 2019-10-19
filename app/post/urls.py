from django.urls import path
from .views import CreatePostView, ListUserTimelinePosts, SeenPostView, LikePostView, BookmarkPostView

urlpatterns = [
    path('new/', CreatePostView.as_view({'post': 'create'}), name='new'),
    path('timeline/', ListUserTimelinePosts.as_view(), name='timeline'),
    path('seen/<int:target_post_id>/', SeenPostView.as_view(), name='seen'),
    path('like/<int:target_post_id>/', LikePostView.as_view(), name='like'),
    path('bookmark/<int:target_post_id>/', BookmarkPostView.as_view(), name='bookmark'),
]
