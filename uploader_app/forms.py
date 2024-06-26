from django import forms

class UploadForm(forms.Form):

    title = forms.CharField(max_length=200)
    file = forms.FileField(required=True)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith('.mp4'):
            raise forms.ValidationError('Only mp4 files are allowed')
        return file
    
    
