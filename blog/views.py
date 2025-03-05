import requests
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
from .websockets import send_post_update
from django.conf import settings



# ✅ ImgBB API kaliti
IMGBB_API_KEY = settings.IMGBB_API_KEY 


def upload_to_imgbb(image_file):
    """📤 ImgBB'ga rasm yuklash va URL qaytarish"""
    try:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": image_file},
        )
        if response.status_code == 200:
            return response.json()["data"]["url"]
        return None
    except requests.RequestException as e:
        logger.error(f"ImgBB upload failed: {e}")
        return None


class PostListCreateView(APIView):
    """📄 Postlarni olish va yaratish"""

    parser_classes = (MultiPartParser, FormParser)  # ✅ Fayllarni yuklash uchun

    def get(self, request):
        """🔍 Postlarni qidirish va olish"""
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
        """📝 Yangi post yaratish"""
        image_url = (
            upload_to_imgbb(request.FILES["image"])
            if "image" in request.FILES
            else None
        )
        background_url = (
            upload_to_imgbb(request.FILES["background_image"])
            if "background_image" in request.FILES
            else None
        )

        data = request.data.copy()
        data["image"] = image_url if image_url else None
        data["background_image"] = background_url if background_url else None

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            send_post_update("created", post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """📄 Bitta postni ko‘rish, o‘zgartirish va o‘chirish"""

    def get(self, request, post_id):
        """🔍 Postni olish"""
        post = Post.objects.filter(id=post_id).first()
        if post:
            return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, post_id):
        """✏️ Postni yangilash"""
        post = Post.objects.filter(id=post_id).first()
        if post:
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                post = serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        """🗑 Postni o‘chirish"""
        post = Post.objects.filter(id=post_id).first()
        if post:
            post.delete()
            # send_post_update("deleted", post)
            return Response(
                {"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
