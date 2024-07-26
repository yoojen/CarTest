from django import forms

from .utils import unpack_code


class GenerateCodeForm(forms.Form):
    phone_number = forms.CharField(
        max_length=10, required=True, 
        help_text="Injiza numero ukoresha uri kwishyura",
        widget=forms.widgets.Input(attrs={"class": "form-control"})
        )

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]
        print(type(data), data.startswith("078"))
        if not ((data.startswith("078")) or  (data.startswith("072") ) or  (data.startswith("073"))):
            raise forms.ValidationError("Phone number not incorrect")
        return data              


class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=10, required=True, help_text="Injiza kode wahawe muri sms kuri telefone yawe",
                           widget=forms.widgets.Input(attrs={"class": "form-control"}))
    

