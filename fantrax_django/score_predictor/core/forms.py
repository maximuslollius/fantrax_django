from django import forms

class UploadForm(forms.Form):
    project_name = forms.FileField()
