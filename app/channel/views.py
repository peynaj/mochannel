from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from app.serializers import ChannelSerializer, PostSerializer
from rest_framework.serializers import Serializer
from app.models import Channel, Follow
from app import queries
from app import responses


# Create your views here.

class CreateChannelView(CreateAPIView):
    """
    post:
    Create new channel
    """

    model = Channel
    permission_classes = (IsAuthenticated,)
    serializer_class = ChannelSerializer


class ListChannelView(ListAPIView):
    """
    get:
        Get channel list
            parameters:
                - name: just_following
                  description: desc ...
                  paramType: query
                  type: boolean
            responseMessages:
                - code: 401
                  message: Not authenticated
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = ChannelSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        user = self.request.user
        just_following = self.request.GET.get('just_following', False)
        queryset = queries.get_channel_list_by_related_counts_and_following_status(
            user.id,
            just_following=True if just_following=='true' else False,
            )
        return queryset


class FollowChannelView(GenericAPIView):
    """
    post:
    Follow channel

    delete:
    Unfollow channel
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer

    def post(self, request, target_channel_id):
        channel = Channel.objects.filter(is_user_self_channel=False).filter(id=target_channel_id)
        if not channel.exists():
            message = 'Channel not found'
            return responses.not_found_json_response(message)
        channel = channel.first()
        if channel.owner == request.user:
            message = 'you can not follow your channel'
            return responses.bad_request_json_response(message)

        if Follow.objects.filter(user=request.user, channel=channel).count() == 0:
            follow = Follow.objects.create(
                user=request.user,
                channel=channel
            )
            follow.save()
            message = 'channel followed successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'channel was previously followed.'
            return responses.successful_json_resonse(message, status=201)

    def delete(self, request, target_channel_id):
        channel = Channel.objects.filter(is_user_self_channel=False).filter(id=target_channel_id)
        if not channel.exists():
            message = 'Channel not found'
            return responses.not_found_json_response(message)
        channel = channel.first()
        follow = channel.follow_set.filter(user_id=request.user.id)
        if follow.count() != 0:
            follow.delete()
            message = 'channel unfollowed successfully'
            return responses.successful_json_resonse(message, status=200)
        else:
            message = 'channel not previously followed.'
            return responses.successful_json_resonse(message, status=200)


class ListChannelPosts(ListAPIView):
    """
    get:
    Get channel posts list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user_id = self.request.user.id
        target_channel_id = self.kwargs.get('target_channel_id')
        queryset = queries.get_channel_posts_list_by_counts_and_status_related_to_special_user(
            target_channel_id, current_user_id
        )
        return queryset

