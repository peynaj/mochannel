from django.db.models import Count, Q, F, Case, When, Value, BooleanField, CharField, IntegerField
from django.contrib.auth.models import User
from app.models import Channel, Post


def get_user_list_by_related_counts_and_following_status(
    special_user_id=None, just_following=False, just_follower=False):
    queryset = User.objects
    queryset = queryset.annotate(
        post_count=Count('channel__post', filter=Q(channel__is_user_self_channel=True), distinct=True,),
    ).annotate(
        follower_count=Count('channel__follow', filter=Q(channel__is_user_self_channel=True), distinct=True,),
    ).annotate(
        following_count=Count('follow', distinct=True,)
    )
    if special_user_id:
        # annotate is_follower
        queryset = queryset.annotate(
            following_special_user_channel_count=Count(
                'follow__channel',
                filter=Q(Q(follow__channel__is_user_self_channel=True) & Q(follow__channel__owner_id=special_user_id)),
                distinct=True,
            )
        )
        queryset = queryset.annotate(
            is_follower=Case(
                When(following_special_user_channel_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        # annotate is_following
        queryset = queryset.annotate(
            self_channel_follow_count_by_special_user=Count(
                'channel__follow',
                filter=Q(Q(channel__is_user_self_channel=True) & Q(channel__follow__user_id=special_user_id)),
                distinct=True,
            )
        )
        queryset = queryset.annotate(
            is_following=Case(
                When(self_channel_follow_count_by_special_user__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        if just_following:
            queryset = queryset.filter(is_following=True)
        if just_follower:
            queryset = queryset.filter(is_follower=True)
    # order queryset
    queryset = queryset.order_by('id')
    return queryset


def get_user_by_related_counts(user_id):
    queryset = User.objects.filter(id=user_id).annotate(
        post_count=Count('channel__post', filter=Q(channel__is_user_self_channel=True), distinct=True,),
    ).annotate(
        follower_count=Count(
            'channel__follow',
            filter=Q(channel__is_user_self_channel=True),
            distinct=True,
        ),
    ).annotate(
        following_count=Count('follow', distinct=True)
    )
    return queryset


def get_channel_list_by_related_counts_and_following_status(
    special_user_id=None, just_following=False
    ):
    queryset = Channel.objects.filter(is_user_self_channel=False)
    if special_user_id and just_following:
        queryset = queryset.filter(follow__user_id=special_user_id)
    queryset = queryset.annotate(
        post_count=Count('post', distinct=True),
    ).annotate(
        follower_count=Count('follow', distinct=True,),
    )
    if special_user_id:
        # annotate is_following
        queryset = queryset.annotate(
            follow_count_by_special_user=Count(
                'follow',
                filter=Q(follow__user_id=special_user_id),
                distinct=True,
            )
        )
        queryset = queryset.annotate(
            is_following=Case(
                When(follow_count_by_special_user__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
    # order queryset
    queryset = queryset.order_by('-created_on')
    return queryset


def get_user_channel_list_by_related_counts_and_following_status(user_id, special_user_id=None):
    queryset = Channel.objects.filter(is_user_self_channel=False, owner_id=user_id)

    queryset = queryset.annotate(
        post_count=Count('post', distinct=True),
    ).annotate(
        follower_count=Count('follow', distinct=True,),
    )
    if special_user_id:
        # annotate is_following
        queryset = queryset.annotate(
            follow_count_by_special_user=Count(
                'follow',
                filter=Q(follow__user_id=special_user_id),
                distinct=True,
            )
        )
        queryset = queryset.annotate(
            is_following=Case(
                When(follow_count_by_special_user__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
    # order queryset
    queryset = queryset.order_by('-created_on')
    return queryset


def get_user_posts_list_by_counts_and_status_related_to_special_user(user_id, special_user_id=None):
    user_self_channel = Channel.objects.filter(
        owner_id=user_id,
        is_user_self_channel=True
    )
    if not user_self_channel.exists():
        user_self_channel = Channel.objects.create(
            owner=user_id,
            is_user_self_channel=True
        )
        user_self_channel.save()
    else:
        user_self_channel = user_self_channel.first()

    queryset = Post.objects.filter(channel=user_self_channel)
    queryset = queryset.annotate(source_type=Value('user', output_field=CharField()))
    queryset = queryset.annotate(source_id=Value(user_id, output_field=IntegerField()))

    queryset = queryset.annotate(seen_count=Count('seen', distinct=True))
    queryset = queryset.annotate(like_count=Count('like', distinct=True))
    queryset = queryset.annotate(bookmark_count=Count('bookmark', distinct=True))

    if special_user_id:
        # is_seen
        queryset = queryset.annotate(
            seen_by_special_user_count=Count(
                'seen',
                filter=Q(seen__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_seen=Case(
                When(seen_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        # is_liked
        queryset = queryset.annotate(
            like_by_special_user_count=Count(
                'like',
                filter=Q(like__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_liked=Case(
                When(like_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        # is_bookmarked
        queryset = queryset.annotate(
            bookmark_by_special_user_count=Count(
                'bookmark',
                filter=Q(bookmark__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_bookmarked=Case(
                When(bookmark_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
    return queryset


def get_channel_posts_list_by_counts_and_status_related_to_special_user(channel_id, special_user_id=None):
    queryset = Post.objects.filter(channel_id=channel_id, channel__is_user_self_channel=False)
    queryset = queryset.annotate(source_type=Value('channel', output_field=CharField()))
    queryset = queryset.annotate(source_id=Value(channel_id, output_field=IntegerField()))

    queryset = queryset.annotate(seen_count=Count('seen', distinct=True))
    queryset = queryset.annotate(like_count=Count('like', distinct=True))
    queryset = queryset.annotate(bookmark_count=Count('bookmark', distinct=True))

    if special_user_id:
        # is_seen
        queryset = queryset.annotate(
            seen_by_special_user_count=Count(
                'seen',
                filter=Q(seen__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_seen=Case(
                When(seen_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        # is_liked
        queryset = queryset.annotate(
            like_by_special_user_count=Count(
                'like',
                filter=Q(like__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_liked=Case(
                When(like_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
        # is_bookmarked
        queryset = queryset.annotate(
            bookmark_by_special_user_count=Count(
                'bookmark',
                filter=Q(bookmark__user_id=special_user_id),
                distinct=True
            )
        ).annotate(
            is_bookmarked=Case(
                When(bookmark_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
    return queryset


def get_user_timeline_post_by_counts_and_status(user_id):
    queryset = Post.objects.filter(Q(channel__follow__user_id=user_id) | Q(channel__owner_id=user_id))
    queryset = queryset.annotate(
        source_type=Case(
            When(channel__is_user_self_channel=True, then=Value('user', output_field=CharField())),
            default=Value('channel', output_field=CharField())
        )
    )
    queryset = queryset.annotate(
        source_id=Case(
            When(channel__is_user_self_channel=True, then=F('channel__owner_id')),
            default=F('channel_id')
        )
    )

    queryset = queryset.annotate(seen_count=Count('seen', distinct=True))
    queryset = queryset.annotate(like_count=Count('like', distinct=True))
    queryset = queryset.annotate(bookmark_count=Count('bookmark', distinct=True))

    # is_seen
    queryset = queryset.annotate(
        seen_by_special_user_count=Count(
            'seen',
            filter=Q(seen__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_seen=Case(
            When(seen_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_liked
    queryset = queryset.annotate(
        like_by_special_user_count=Count(
            'like',
            filter=Q(like__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_liked=Case(
            When(like_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_bookmarked
    queryset = queryset.annotate(
        bookmark_by_special_user_count=Count(
            'bookmark',
            filter=Q(bookmark__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_bookmarked=Case(
            When(bookmark_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    queryset = queryset.order_by('-created_on')
    return queryset

def get_user_liked_posts_list(user_id):
    queryset = Post.objects.filter(like__user_id=user_id)

    queryset = queryset.annotate(
        source_type=Case(
            When(channel__is_user_self_channel=True, then=Value('user', output_field=CharField())),
            default=Value('channel', output_field=CharField())
        )
    )
    queryset = queryset.annotate(
        source_id=Case(
            When(channel__is_user_self_channel=True, then=F('channel__owner_id')),
            default=F('channel_id')
        )
    )

    queryset = queryset.annotate(seen_count=Count('seen', distinct=True))
    queryset = queryset.annotate(like_count=Count('like', distinct=True))
    queryset = queryset.annotate(bookmark_count=Count('bookmark', distinct=True))

    # is_seen
    queryset = queryset.annotate(
        seen_by_special_user_count=Count(
            'seen',
            filter=Q(seen__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_seen=Case(
            When(seen_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_liked
    queryset = queryset.annotate(
        like_by_special_user_count=Count(
            'like',
            filter=Q(like__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_liked=Case(
            When(like_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_bookmarked
    queryset = queryset.annotate(
        bookmark_by_special_user_count=Count(
            'bookmark',
            filter=Q(bookmark__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_bookmarked=Case(
            When(bookmark_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # order
    queryset = queryset.order_by('-created_on')
    return queryset


def get_user_bookmarked_posts_list(user_id):
    queryset = Post.objects.filter(bookmark__user_id=user_id)

    queryset = queryset.annotate(
        source_type=Case(
            When(channel__is_user_self_channel=True, then=Value('user', output_field=CharField())),
            default=Value('channel', output_field=CharField())
        )
    )
    queryset = queryset.annotate(
        source_id=Case(
            When(channel__is_user_self_channel=True, then=F('channel__owner_id')),
            default=F('channel_id')
        )
    )

    queryset = queryset.annotate(seen_count=Count('seen', distinct=True))
    queryset = queryset.annotate(like_count=Count('like', distinct=True))
    queryset = queryset.annotate(bookmark_count=Count('bookmark', distinct=True))

    # is_seen
    queryset = queryset.annotate(
        seen_by_special_user_count=Count(
            'seen',
            filter=Q(seen__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_seen=Case(
            When(seen_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_liked
    queryset = queryset.annotate(
        like_by_special_user_count=Count(
            'like',
            filter=Q(like__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_liked=Case(
            When(like_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # is_bookmarked
    queryset = queryset.annotate(
        bookmark_by_special_user_count=Count(
            'bookmark',
            filter=Q(bookmark__user_id=user_id),
            distinct=True
        )
    ).annotate(
        is_bookmarked=Case(
            When(bookmark_by_special_user_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    )
    # order
    queryset = queryset.order_by('-created_on')
    return queryset
