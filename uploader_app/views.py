from django.shortcuts import render
from django.views import View
from django.core.files.storage import FileSystemStorage
import requests
import subprocess
from django.http import HttpResponse, JsonResponse
import os
from django.conf import settings
from slugify import slugify
from .forms import UploadForm
import boto3
from django.http import FileResponse, Http404

# from .models import MPDFile
# Create your views here.

# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     region_name=settings.AWS_S3_REGION_NAME,
# )

def handle_upload_video(file, title):

    upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{title}_{file.name}")
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path


def process_video(file_path, filename):

    output_dir = os.path.join(settings.MEDIA_ROOT, f'dash_output') 
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "video.mpd")
    filename = os.path.basename(file_path).split('.')[0]

    command = [
        'ffmpeg', '-i', file_path, '-map', '0', '-s:v', '1920x1080', '-c:v', 'libx264', '-b:v', '2400k', '-an',
        '-f', 'dash', '-seg_duration', '4', output_file
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    return result, output_file


def delete_upload_file(file):
    if os.path.exists(file):
        os.remove(file)




class VideoUploadView(View):

    def get(self, request):

        form = UploadForm()
        return render(request, 'upload_form.html', {'form': form})

    def post(self, request):

        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():

            title = form.cleaned_data['title']
            file = form.cleaned_data['file']    # print(video_file.name)
            filename = f"{title}_{file}"
            # fs = FileSystemStorage()
            # filename = fs.save(title, file)
            # uploaded_file = fs.url(filename)

            # base_path = os.getcwd() + uploaded_file
            # # print(base_path)
            # s3_client.upload_fileobj(
            #     file,
            #     settings.AWS_STORAGE_BUCKET_NAME,
            #     f"videos/{filename}",
            # )
            file_path = handle_upload_video(file, title)
            result, output_file = process_video(file_path, title)

            if result.returncode != 0:
                return render(request, 'upload_success.html',  {'error': 'Processing failed', 'details': result.stderr})

            # MPDFile.objects.create(
            #     title=title,
            #     mpd=output_file,
            # )

            delete_upload_file(file_path)
            # output_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/videos/{filename}"
            return render(request, 'upload_success.html', {'message': 'Processing complete'})
            # return Response({'message': 'Upload Successfull'}, status=status.HTTP_201_CREATED)
        else:
            return render(request, 'upload_success.html', {'message': 'No video file provided'})

# def list_videos(request):
#     mpd_files = MPDFile.objects.all()
#     return render(request, 'list_videos.html', {'mpd_files': mpd_files})

def serve_mpd(request):
    try:
        print("Serving mpd")
        file_path = os.path.join(settings.MEDIA_ROOT, 'dash_output', 'video.mpd')
        return FileResponse(open(file_path, 'rb'), content_type='application/dash+xml')
    except FileNotFoundError:
        raise Http404("MPD File Not Found")

def serve_segments(request, segment):
    try:
        print("Serving segments")
        file_path = os.path.join(settings.MEDIA_ROOT, 'dash_output', segment)
        return FileResponse(open(file_path, 'rb'), content_type='video/iso.segment')
    except FileNotFoundError:
        raise Http404("Segment Not Found")

def video_player(request):
    return render(request, 'video_stream.html')
