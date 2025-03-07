from rest_framework import serializers
from .models import Post, Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "description", "content", "section_image", "order"]


class PostSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True)

    class Meta:
        model = Post
        fields = ["id", "title", "image", "background_image", "created_at", "sections"]

    def create(self, validated_data):
        sections_data = validated_data.pop("sections")
        post = Post.objects.create(**validated_data)

        for order, section_data in enumerate(sections_data):
            Section.objects.create(post=post, order=order, **section_data)

        return post
