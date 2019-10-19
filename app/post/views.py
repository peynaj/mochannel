from rest_framework.generics import ListAPIView, GenericAPIView
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from app.serializers import PostSerializer
from rest_framework.serializers import Serializer
from app.models import Channel, Follow, Post, Seen, Like, Bookmark
from app import queries
from app import responses
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.viewsets import ModelViewSet
import json


# Create your views here.


class CreatePostView(ModelViewSet):
    """
    post:
    Create new post
    """

    model = Post
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = request.user
        data = {}
        if serializer.is_valid():
            serializer.clean()
            data = serializer.validated_data
        source_channel_id = None
        source_type = data.get('source_type')
        if source_type == 'user':
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
            source_channel_id = user_self_channel.id
        elif source_type == 'channel':
            source_channel_id = data.get('source_id')
        post = Post.objects.create(
            channel_id=source_channel_id,
            text=data.get('text', ''),
            file=data.get('file'),
        )
        post.save()
        resp = dict(
            id=post.id,
            file=post.file.url if post.file else None,
            text=post.text,
            created_on=str(post.created_on),
            source_type=data.get('source_type'),
            source_id=data.get('source_id'),
        )
        return HttpResponse(json.dumps(resp), status=201, content_type='application/json')

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     serializer.clean()
    #     data = serializer.validated_data
    #     print('data:', data)
    #     print('file:', data.get('file'))
    #     print('-----')
    #     source_channel_id = None
    #     source_type = data.get('source_type')
    #     if source_type == 'user':
    #         user_self_channel = Channel.objects.filter(
    #             owner=user,
    #             is_user_self_channel=True
    #         )
    #         if not user_self_channel.exists():
    #             user_self_channel = Channel.objects.create(
    #                 owner=user,
    #                 is_user_self_channel=True
    #             )
    #             user_self_channel.save()
    #         else:
    #             user_self_channel = user_self_channel.first()
    #         source_channel_id = user_self_channel.id
    #     elif source_type == 'channel':
    #         source_channel_id = data.get('source_id')
    #     post = Post.objects.create(
    #         channel_id=source_channel_id,
    #         text=data.get('text', ''),
    #         file=data.get('file'),
    #     )
    #     post.save()
    #     self.file = data.get('file')
    #     print(self.file)
    #     print('-----')


class ListUserTimelinePosts(ListAPIView):
    """
    get:
    Get user timeline posts list
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        current_user_id = self.request.user.id
        queryset = queries.get_user_timeline_post_by_counts_and_status(current_user_id)
        return queryset


class SeenPostView(GenericAPIView):
    """
    post:
    Seen post

    delete:
    Undo seen post
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer

    def post(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()
        if target_post.channel.owner == self.request.user:
            message = 'You can not seen your post!'
            return responses.bad_request_json_response(message)

        if Seen.objects.filter(user=request.user, post=target_post).count() == 0:
            seen = Seen.objects.create(
                user=request.user,
                post=target_post,
            )
            seen.save()
            message = 'post seen successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was previously seen.'
            return responses.successful_json_resonse(message, status=201)

    def delete(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()
        seen = Seen.objects.filter(user=request.user, post=target_post)
        if seen.exists():
            seen.delete()
            message = 'undo post seen successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was not previously seen'
            return responses.successful_json_resonse(message, status=201)


class LikePostView(GenericAPIView):
    """
    post:
    Like post

    delete:
    Undo like post
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer

    def post(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()

        # user allowed to like herself posts!
        '''
        if target_post.channel.owner == self.request.user:
            message = 'You can not like your post!'
            return responses.bad_request_json_response(message)
        '''

        if Like.objects.filter(user=request.user, post=target_post).count() == 0:
            like = Seen.objects.create(
                user=request.user,
                post=target_post,
            )
            like.save()
            message = 'post liked successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was previously liked'
            return responses.successful_json_resonse(message, status=201)

    def delete(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()
        like = Like.objects.filter(user=request.user, post=target_post)
        if like.exists():
            like.delete()
            message = 'undo post like successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was not previously liked'
            return responses.successful_json_resonse(message, status=201)


class BookmarkPostView(GenericAPIView):
    """
    post:
    Bookmark post

    delete:
    Undo bookmark post
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer

    def post(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()

        # user allowed to bookmark herself posts!
        '''
        if target_post.channel.owner == self.request.user:
            message = 'You can not bookmark your post!'
            return responses.bad_request_json_response(message)
        '''

        if Bookmark.objects.filter(user=request.user, post=target_post).count() == 0:
            bookmark = Bookmark.objects.create(
                user=request.user,
                post=target_post,
            )
            bookmark.save()
            message = 'post bookmarked successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was previously bookmarked'
            return responses.successful_json_resonse(message, status=201)

    def delete(self, request, target_post_id):
        target_post = Post.objects.filter(id=target_post_id)
        if not target_post.exists():
            message = 'post not found'
            return responses.not_found_json_response(message)
        target_post = target_post.first()
        bookmark = Bookmark.objects.filter(user=request.user, post=target_post)
        if bookmark.exists():
            bookmark.delete()
            message = 'undo post bookmark successfully'
            return responses.successful_json_resonse(message, status=201)
        else:
            message = 'post was not previously bookmarked'
            return responses.successful_json_resonse(message, status=201)

