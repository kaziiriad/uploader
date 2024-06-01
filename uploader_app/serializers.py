from rest_framework import serializers

class UploadFile:
    def __init__(self, name, file):
        self.name = name
        self.file = file

    def __str__(self):
        return self.name

class UploadFileSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100)
    file = serializers.FileField(max_length=None, allow_empty_file=False, use_url=True)

    def create(self, validated_data):
        return UploadFile(**validated_data)

    