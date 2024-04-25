from django import forms
from django.core.exceptions import ValidationError

from .models import CompanyUser, Customer, Label, Note


class CompanyUserForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': "form-control", 'placeholder': 'Enter Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': "form-control", 'placeholder': 'Confirm Password'}))

    field_order = ['name', 'phone']

    class Meta:
        model = CompanyUser
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Enter CompanyUser Name'}),
            'phone': forms.TextInput(
                attrs={'type': 'number', 'class': "form-control", 'placeholder': 'Enter Phone Number'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match')
        return password2

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data["password"])
        instance.is_superuser = False
        instance.email = '-'
        if commit:
            instance.save()
        return instance


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('company_user',)
        widgets = {
            'name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Enter Customer Name'}),
            'phone': forms.TextInput(
                attrs={'type': 'number', 'class': "form-control", 'placeholder': 'Enter Phone Number'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user is not None:
            instance.company_user = user
        else:
            raise ValidationError('Company login is required')

        if commit:
            instance.save()
        return instance


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        exclude = ('created_by', 'customers')
        widgets = {
            'name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Enter Label Name'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user is not None:
            instance.created_by = user
        else:
            raise ValidationError('Company login is required')

        if commit:
            instance.save()
        return instance


class LabelToCustomer(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.customer_id = kwargs.pop('customer_id', None)
        super(LabelToCustomer, self).__init__(*args, **kwargs)
        self.fields['label'] = forms.ModelChoiceField(queryset=user.labels.all(), empty_label="Select Label",widget=forms.Select(attrs={'class': "form-control", 'placeholder': 'Enter Note description'}))

    def save(self):
        selected_label = self.cleaned_data['label']
        customer = Customer.objects.get(pk=self.customer_id)

        customer.labels.add(selected_label)
        customer.save()


class NoteToCustomer(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.customer_id = kwargs.pop('customer_id', None)
        super(NoteToCustomer, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        exclude = ('customer',)
        widgets = {
            'description': forms.Textarea(attrs={'class': "form-control", 'placeholder': 'Enter Note description'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.customer_id is not None:
            instance.customer = Customer.objects.get(pk=self.customer_id)
        else:
            raise ValidationError("Customer is required")

        if commit:
            instance.save()
        return instance
