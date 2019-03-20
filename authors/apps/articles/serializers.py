from rest_framework import serializers

from authors.apps.profiles.serializers import ProfileSerializer

from .models import Article, Like, Snapshot, ThreadedComment


class TheArticleSerializer(serializers.ModelSerializer):

    reading_time = serializers.ReadOnlyField(source='get_reading_time')

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body', 'draft', 'slug', 'reading_time',
            'editing', 'description', 'published', 'activated',
            "created_at", "updated_at", 'author'
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        '''Create a new Article instance, given the accepted data.'''
        article = Article.objects.create(**validated_data)
        return article

    def update(self, instance, validated_data):
        '''Enable update on articles already existing and returns it.'''

        instance.title = validated_data.get(
            'title', instance.title
        )
        instance.body = validated_data.get('body', instance.body)
        instance.draft = validated_data.get(
            'draft', instance.draft
        )
        instance.editing = validated_data.get('editing', instance.editing)
        instance.description = validated_data.get(
            'description', instance.description
        )
        instance.published = validated_data.get(
            'published', instance.published
        )
        instance.activated = validated_data.get(
            'activated', instance.activated
        )
        instance.save()
        return instance


class LikesSerializer(serializers.ModelSerializer):
    """
    Serializers for likes
    """
    class Meta():
        model = Like
        fields = ('id', 'user_id', 'article_id', 'is_like')
        read_only_fields = ['id']


class ArticleCommentInputSerializer(serializers.ModelSerializer):
    """Seriliazes input data and creates a new article comment."""
    highlight = serializers.CharField(min_length=1, required=False)

    class Meta:
        model = ThreadedComment
        fields = ('article', 'author', 'body', "highlight")
        extra_kwargs = {'article': {'required': True}}


class CommentCommentInputSerializer(serializers.ModelSerializer):
    """Serializes input data and creates a new comment comment."""
    class Meta:
        model = ThreadedComment
        fields = ('article', 'comment', 'author', 'body')
        extra_kwargs = {'comment': {'required': True}}


class SnapshotSerializer(serializers.ModelSerializer):
    """Serializer for displaying comment snapshots."""
    class Meta:
        model = Snapshot
        fields = ('id', 'highlight', 'body', 'timestamp')


class EmbededCommentOutputSerializer(serializers.ModelSerializer):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    edit_history = SnapshotSerializer(many=True, source='snapshots')
    is_highlight_comment = serializers.BooleanField(
        source="is_article_highlighted")

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited',
                  'is_highlight_comment', 'highlight', 'body',
                  'author', 'edit_history')


class ThreadedCommentOutputSerializer(serializers.ModelSerializer):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    comments = EmbededCommentOutputSerializer(many=True)
    edit_history = SnapshotSerializer(many=True, source='snapshots')
    is_highlight_comment = serializers.BooleanField(
        source="is_article_highlighted")

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited', 'body',
                  'is_highlight_comment', 'highlight', 'author',
                  'edit_history', 'comments')
