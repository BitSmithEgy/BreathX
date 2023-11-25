# forms.py
from django import forms
from .models import UploadedImage

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
