from django import forms



class UserInfoForm(forms.Form):
    first_name = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Vārds:'}))
    last_name = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Uzvārds:'}))
    birth_date = forms.DateField(label='', widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email:'}))