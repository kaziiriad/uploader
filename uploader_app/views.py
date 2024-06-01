from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from .encoder_1 import encode
import requests
import subprocess
from django.http import JsonResponse
import os
from django.conf import settings
from slugify import slugify

# Create your views here.
def process_video(file_path):

    output_dir = 'dash_output_' + slugify(os.path.basename(file_path)[:-4])
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "video.mpd")
    command = [
        'ffmpeg', '-i', file_path, '-map', '0', '-s:v', '1920x1080', '-c:v', 'libx264', '-b:v', '2400k', '-an', '-f', 'dash', output_file
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    return result, output_file


class VideoUploadView(APIView):

    def get(self, request):

        return render(request, 'upload_form.html')

    def post(self, request):

        video_file = request.FILES.get('file')
        if video_file:
            # print(video_file.name)

            fs = FileSystemStorage()
            filename = fs.save(video_file.name, video_file)
            uploaded_file = fs.url(filename)

            base_path = os.getcwd() + uploaded_file
            # print(base_path)
            result, output_file = process_video(base_path)
            
            if result.returncode != 0:
                return Response({'error': 'Processing failed', 'details': result.stderr}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'message': 'Processing complete', 'output_file': output_file}, status=status.HTTP_201_CREATED)
            # return Response({'message': 'Upload Successfull'}, status=status.HTTP_201_CREATED)
            
        else:
            
            return Response({'message': 'No video file provided'}, status=status.HTTP_400_BAD_REQUEST)


    