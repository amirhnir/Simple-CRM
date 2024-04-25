from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from .forms import CompanyUserForm, CustomerForm, LabelForm, LabelToCustomer, NoteToCustomer
from .models import CompanyUser, Customer, Label


def main_page(request):
    return render(request, 'main/main.html')


@method_decorator(login_required, name='dispatch')
class DashboardView(View):

    def get(self, request):
        customers = request.user.customers.all()
        labels = request.user.labels.all()
        customer_form = CustomerForm()
        label_form = LabelForm()
        return render(request, 'dashboard/main.html',
                      {'customers': customers, 'label_form': label_form, 'labels': labels,
                       'customer_form': customer_form})

    # Creating New Customer
    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
        return redirect('dashboard')


@method_decorator(login_required, name='dispatch')
class CustomerDetailView(View):

    def get(self, request, id):
        label_form = LabelToCustomer(user=request.user)
        note_form = NoteToCustomer()
        customer = request.user.customers.get(pk=id)
        labels = customer.labels.all()
        notes = customer.notes.all()
        return render(request, 'dashboard/customer-detail.html',
                      {'notes': notes, 'note_form': note_form, 'labels': labels, 'customer': customer,
                       "label_form": label_form})

    # Adding or removing a Label to/from a customer
    # Adding a Note to a customer
    def post(self, request, id):
        type = request.POST.get('type', 'label')
        if type == 'label':
            remove = request.POST.get('remove', False)
            form = LabelToCustomer(request.POST, user=request.user, customer_id=id)
            if form.is_valid():
                if not remove:
                    form.save()
                else:
                    label = form.cleaned_data.get('label')
                    customer = Customer.objects.get(pk=id)
                    customer.labels.remove(label)
                    customer.save()

        elif type == 'note':
            form = NoteToCustomer(request.POST, customer_id=id)
            if form.is_valid():
                form.save()

        return redirect('customer-detail', id=id)


class LoginView(View):

    def get(self, request):
        form = CompanyUserForm()
        return render(request, 'main/login.html', {'form': form})

    # Login and Register
    def post(self, request):
        next_url = request.GET.get('next', 'dashboard')
        form = CompanyUserForm(request.POST)
        phone = request.POST.get('phone', None)
        password = request.POST.get('password', None)
        company_user = CompanyUser.objects.filter(phone=phone).first()

        if company_user:
            authenticated_user = authenticate(request, phone=phone, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect(next_url)
            else:
                form.add_error(None, "Invalid phone number or password.")
        else:
            if form.is_valid():
                form.save()
                new_company_user = authenticate(request, phone=phone, password=password)
                if new_company_user:
                    login(request, new_company_user)
                    return redirect(next_url)

        return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('main_page')


@method_decorator(login_required, name='dispatch')
class LabelView(View):

    # Creating Label
    def post(self, request):
        form = LabelForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
        return redirect('dashboard')
