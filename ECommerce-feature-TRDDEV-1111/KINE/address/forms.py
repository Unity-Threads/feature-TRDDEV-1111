from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name", "mobile_number", "address_line1", "address_line2","landmark",
            "city", "state", "country", "pincode"
        ]
