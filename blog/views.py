import requests
import json
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer

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
                | Q(section_elements__value__icontains=search)
            ).distinct()

        return Response(
            PostSerializer(posts, many=True).data, status=status.HTTP_200_OK
        )

    def post(self, request):
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
            "sections": (
                sections_data if sections_data else None
            ),  # 🔥 Agar bo‘sh bo‘lsa, eski sections o‘zgarishsiz qoladi
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
