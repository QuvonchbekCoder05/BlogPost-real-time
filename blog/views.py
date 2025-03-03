from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_post_update(action, post):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "posts_updates",
        {"type": "post_message", "action": action, "post": PostSerializer(post).data},
    )


class PostListCreateView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        posts = (
            Post.objects.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(content__icontains=search)
            )
            if search
            else Post.objects.all()
        )
        return Response(
            PostSerializer(posts, many=True).data, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            send_post_update("created", post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                post = serializer.save()
                send_post_update("updated", post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            post.delete()
            send_post_update("deleted", post)
            return Response(
                {"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
