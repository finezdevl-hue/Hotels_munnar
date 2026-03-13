from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'email', 'phone', 'check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'check_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'}),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests? (optional)'
            }),
        }
