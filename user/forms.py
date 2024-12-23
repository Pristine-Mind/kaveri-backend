from django import forms
from .models import BeerClubMember, ContactMessage


class BeerClubSignUpForm(forms.ModelForm):
    class Meta:
        model = BeerClubMember
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'message']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("This field is required")
        return email


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email
