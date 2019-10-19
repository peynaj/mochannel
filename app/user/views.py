from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.serializers import UserSerializer, PostSerializer, ChannelSerializer
from rest_framework.serializers import Serializer
from app.models import Channel, Follow
from django.contrib.auth.models import User
from app import queries
from app import responses


# Create your views here.

class CreateUserView(CreateAPIView):
    """
    post:
    Register new user
    """

    model = User
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class ListUserView(ListAPIView):
    """
    get:
    Get users list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        user = self.request.user
        just_following = self.request.GET.get('just_following', False)
        just_follower = self.request.GET.get('just_follower', False)
        queryset = queries.get_user_list_by_related_counts_and_following_status(
            user.id,
            just_following=True if just_following=='true' else False,
            just_follower=True if just_follower=='true' else False,
            )
        return queryset


class Whoami(RetrieveAPIView):
    """
    get:
    Get current logged-in user
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        user_self_channel = Channel.objects.filter(
            owner=user,
            is_user_self_channel=True
        )
        if not user_self_channel.exists():
            user_self_channel = Channel.objects.create(
                owner=user,
                is_user_self_channel=True
            )
            user_self_channel.save()
        else:
            user_self_channel = user_self_channel.first()

        query = queries.get_user_by_related_counts(user.id)
        query = query.first()
        serializer = UserSerializer(query, context={'request': request})
        return Response(serializer.data)


class FollowUserView(GenericAPIView):
    """
    post:
    Follow user

    delete:
    Unfollow user
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer

    def post(self, request, target_user_id):
        if target_user_id == request.user.id:
            message = 'You can not follow yourself!'
            return responses.bad_request_json_response(message)
        target_user = User.objects.filter(id=target_user_id)
        if not target_user.exists():
            message = 'user not found'
            return responses.not_found_json_response(message)
        target_user = target_user.first()
        user_self_channel = Channel.objects.filter(
            owner=target_user,
            is_user_self_channel=True
        )
        if not user_self_channel.exists():
            user_self_channel = Channel.objects.create(
                owner=target_user,
                is_user_self_channel=True
            )
            user_self_channel.save()
        else:
            user_self_channel = user_self_channel.first()
        if Follow.objects.filter(user=request.user, channel=user_self_channel).count() == 0:
            follow = Follow.objects.create(
                user=request.user,
                channel=user_self_channel
            )
            follow.save()
            message = 'user followed successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'user was previously followed.'
            return responses.successful_json_resonse(message, status=201)

    def delete(self, request, target_user_id):
        if target_user_id == request.user.id:
            message = 'You can not unfollow yourself!'
            return responses.bad_request_json_response(message)
        target_user = User.objects.filter(id=target_user_id)
        if not target_user.exists():
            message = 'user not found'
            return responses.not_found_json_response(message)
        target_user = target_user.first()
        user_self_channel = Channel.objects.filter(
            owner=target_user,
            is_user_self_channel=True
        )
        if not user_self_channel.exists():
            user_self_channel = Channel.objects.create(
                owner=target_user,
                is_user_self_channel=True
            )
            user_self_channel.save()
        else:
            user_self_channel = user_self_channel.first()
        follow = user_self_channel.follow_set.filter(user_id=request.user.id)
        if follow.count() != 0:
            follow.delete()
            message = 'user unfollowed successfully'
            return responses.successful_json_resonse(message, status=200)
        else:
            message = 'user not previously followed.'
            return responses.successful_json_resonse(message, status=200)


class ListUserPosts(ListAPIView):
    """
    get:
    Get user posts list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user = self.request.user
        target_user_id = self.kwargs.get('target_user_id')
        queryset = queries.get_user_posts_list_by_counts_and_status_related_to_special_user(target_user_id, current_user)
        return queryset


class ListUserChannelsView(ListAPIView):
    """
    get:
    Get user channels list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = ChannelSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user_id = self.request.user.id
        target_user_id = self.kwargs.get('target_user_id')
        queryset = queries.get_user_channel_list_by_related_counts_and_following_status(target_user_id, current_user_id)
        return queryset


class ListUserLikedPostsView(ListAPIView):
    """
    get:
    Get user liked posts list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user_id = self.request.user.id
        queryset = queries.get_user_liked_posts_list(current_user_id)
        return queryset


class ListUserBookmarkedPostsView(ListAPIView):
    """
    get:
    Get user bookmarked posts list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user_id = self.request.user.id
        queryset = queries.get_user_bookmarked_posts_list(current_user_id)
        return queryset

