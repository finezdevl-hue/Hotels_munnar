from django import forms
from .models import Hotel, HotelImage, Room, Review


class HotelSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Hotel name or destination...',
        'class': 'form-control form-control-lg'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'form-control'
    }))
    check_in = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    check_out = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    guests = forms.IntegerField(required=False, min_value=1, initial=2, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '1',
        'max': '20'
    }))
    stars = forms.ChoiceField(required=False, choices=[('', 'Any Stars')] + [(i, f'{i} Stars') for i in range(1, 6)],
                               widget=forms.Select(attrs={'class': 'form-select'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Min price',
        'class': 'form-control'
    }))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Max price',
        'class': 'form-control'
    }))


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        exclude = ['owner', 'slug', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'stars': forms.Select(attrs={'class': 'form-select'}),
            'amenities': forms.CheckboxSelectMultiple(),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HotelImageForm(forms.ModelForm):
    class Meta:
        model = HotelImage
        fields = ['image', 'caption', 'is_main', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['hotel']
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'size_sqm': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.CheckboxSelectMultiple(),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bed_type': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'cleanliness', 'service', 'location', 'value']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)],
                                   attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
            'cleanliness': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)],
                                        attrs={'class': 'form-select'}),
            'service': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)],
                                    attrs={'class': 'form-select'}),
            'location': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)],
                                     attrs={'class': 'form-select'}),
            'value': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)],
                                  attrs={'class': 'form-select'}),
        }
