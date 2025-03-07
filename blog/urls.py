from django.urls import path
from .views import PostListCreateView, PostDetailView, PingView

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="post-list"),
    path("posts/<int:post_id>/", PostDetailView.as_view(), name="post-detail"),
    path("ping/", PingView.as_view(), name="ping"),  # 🔁 Ping API
]
