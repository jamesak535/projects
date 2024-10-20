from django import forms
from .models import Bill

class BillUploadForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['image']

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput)
