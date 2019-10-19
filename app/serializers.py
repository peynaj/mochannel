from django.contrib.auth.models import User
from app.models import Channel, Post
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email','first_name', 'last_name', 'date_joined', 'password',
                  'post_count', 'follower_count', 'following_count', 'is_follower', 'is_following',
                  )

    password = serializers.CharField(write_only=True)
    # read_only fields
    id = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    post_count = serializers.IntegerField(read_only=True)
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_follower = serializers.BooleanField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
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
        user.save()

        return user


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'owner_id', 'title', 'description', 'created_on',
                  'post_count', 'follower_count', 'is_following',
                  )

    title = serializers.CharField(max_length=64, required=True)
    description = serializers.CharField(max_length=256, required=False)
    # read_only fields
    id = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    post_count = serializers.IntegerField(read_only=True)
    follower_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        channel = Channel.objects.create(
            owner=user,
            is_user_self_channel=False,
            title=validated_data.get('title'),
            description=validated_data.get('description', '')
        )
        channel.save()
        return channel


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'source_type', 'source_id', 'text', 'file', 'created_on',
                  'is_seen', 'is_liked', 'is_bookmarked',
                  'seen_count', 'like_count', 'bookmark_count',
                  )

    source_type = serializers.CharField(max_length=64, required=True)
    source_id = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=1000, required=False)
    file = serializers.FileField(max_length=500, allow_empty_file=True, required=False)

    # read_only fields
    id = serializers.IntegerField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    seen_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    bookmark_count = serializers.IntegerField(read_only=True)
    is_seen = serializers.BooleanField(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)

    def clean(self):
        data = self.data
        files = self.context['request'].FILES
        # if 'file' in files:
        #     self.file = files['file']
        if not (files.get('file') or data.get('text')):
            raise serializers.ValidationError("file or text is required")
        source_type = data.get('source_type')
        if source_type == 'user':
            if data.get('source_id'):
                if self.context['request'].user.id != data.get('source_id'):
                    raise serializers.ValidationError("you can not post for another user")
            else:
                self.data['source_id'] = self.context['request'].user.id
                data['source_id'] = self.context['request'].user.id
        elif source_type == 'channel':
            if not data.get('source_id'):
                raise serializers.ValidationError("source_id is required in channel mode")
            channel = Channel.objects.filter(id=data.get('source_id'), is_user_self_channel=False)
            if not channel.exists():
                raise serializers.ValidationError("channel not found")
            channel = channel.first()
            if channel.owner_id != self.context['request'].user.id:
                raise serializers.ValidationError("you can not post for other people channel")

        else:
            raise serializers.ValidationError("source must be user or channel")


