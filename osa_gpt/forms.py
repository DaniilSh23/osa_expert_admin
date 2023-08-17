from django import forms


class NewApplicationForm(forms.Form):
    """
    Форма для создания новой заявки
    """
    tlg_id = forms.CharField(max_length=15)
    client_name = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=50)
    description = forms.CharField(max_length=1000)
