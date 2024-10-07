from django import forms
from .models import Bill

class BillUploadForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['image']
