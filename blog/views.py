import os
import environ
import requests
import json
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer

# `.env` faylni o‘qish
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 🔥 `.env` dan `PASSWORD` ni yuklash
PASSWORD = env("PASSWORD")


def check_password(request):
    """🔒 Header orqali kelayotgan `PASSWORD` ni tekshirish"""
    client_password = request.headers.get(
        "PASSWORD"
    )  # 🔥 Foydalanuvchidan kelgan parol
    system_password = PASSWORD  # 🔥 `.env` dan yuklangan parol

    if not client_password or client_password != system_password:
        return (
            False  # ❌ Agar `PASSWORD` kelmasa yoki noto‘g‘ri bo‘lsa, ruxsat berilmaydi
        )

    return True  # ✅ Parol to‘g‘ri bo‘lsa, ruxsat beriladi


IMGBB_API_KEY = "112af12bdf2b321282827fe1da784f74"


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
    except requests.RequestException:
        return None


class PostListCreateView(APIView):
    """📄 Postlarni olish va yaratish"""

    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        search = request.GET.get("search", "")
        posts = Post.objects.all()

        if search:
            posts = posts.filter(
                Q(title__icontains=search)
                | Q(sections__description__icontains=search)
                | Q(sections__content__icontains=search)
            ).distinct()

        return Response(
            PostSerializer(posts, many=True).data, status=status.HTTP_200_OK
        )

    def post(self, request):
        """🔒 `POST` faqat `PASSWORD` to‘g‘ri bo‘lsa ishlaydi"""
        if not check_password(request):
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Rasm yuklash
        image_url = (
            upload_to_imgbb(request.FILES.get("image"))
            if "image" in request.FILES
            else None
        )
        background_url = (
            upload_to_imgbb(request.FILES.get("background_image"))
            if "background_image" in request.FILES
            else None
        )

        # ✅ SECTIONS FORMATINI TO‘G‘RILASH
        sections_data = []
        i = 0
        while f"sections[{i}][description]" in request.data:
            sections_data.append(
                {
                    "description": request.data.get(f"sections[{i}][description]", ""),
                    "content": request.data.get(f"sections[{i}][content]", ""),
                    "section_image": (
                        upload_to_imgbb(
                            request.FILES.get(f"sections[{i}][section_image]")
                        )
                        if f"sections[{i}][section_image]" in request.FILES
                        else None
                    ),
                }
            )
            i += 1

        # Serializer uchun ma’lumot tayyorlash
        data = {
            "title": request.data.get("title"),
            "image": image_url,
            "background_image": background_url,
            "sections": sections_data,
        }

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """📄 Bitta postni ko‘rish, yangilash va o‘chirish"""

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, post_id):
        """🔒 `PUT` faqat `PASSWORD` to‘g‘ri bo‘lsa ishlaydi"""
        if not check_password(request):
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        post = Post.objects.filter(id=post_id).first()
        if not post:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 🔥 Rasm fayllarini yuklash
        image_url = (
            upload_to_imgbb(request.FILES.get("image"))
            if "image" in request.FILES
            else post.image
        )
        background_url = (
            upload_to_imgbb(request.FILES.get("background_image"))
            if "background_image" in request.FILES
            else post.background_image
        )

        # ✅ SECTIONS FORMATINI TO‘G‘RILASH
        sections_data = []
        i = 0
        while f"sections[{i}][description]" in request.data:
            sections_data.append(
                {
                    "description": request.data.get(f"sections[{i}][description]", ""),
                    "content": request.data.get(f"sections[{i}][content]", ""),
                    "section_image": (
                        upload_to_imgbb(
                            request.FILES.get(f"sections[{i}][section_image]")
                        )
                        if f"sections[{i}][section_image]" in request.FILES
                        else None
                    ),
                }
            )
            i += 1

        # ✅ Yangi ma’lumotlarni serializerga uzatamiz
        data = {
            "title": request.data.get("title", post.title),
            "image": image_url,
            "background_image": background_url,
            "sections": sections_data if sections_data else None,
        }

        serializer = PostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            post.delete()
            return Response(
                {"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


class PingView(APIView):
    def get(self, request):
        return Response({"message": "Server is running!"}, status=status.HTTP_200_OK)
