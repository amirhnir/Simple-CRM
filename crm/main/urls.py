from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('login', LoginView.as_view(), name='login'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('dashboard/label', LabelView.as_view(), name='label'),
    path('logout', logout_view, name='logout'),
    path('dashboard/customer-detail/<id>', CustomerDetailView.as_view(), name='customer-detail'),
]
