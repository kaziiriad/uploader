from django.urls import path
from . import views

urlpatterns = [
    # path('', views.list_videos, name='home'),
    path('upload', views.VideoUploadView.as_view(), name='video-upload-html'),
    path('video/', views.serve_mpd,  name='serve-mpd'),
    path('video/<str:segment>', views.serve_segments, name='serve-segments'),
    path('', views.video_player, name='stream'),
]
