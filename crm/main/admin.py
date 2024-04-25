from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CompanyUser)
admin.site.register(Label)
admin.site.register(Customer)
admin.site.register(Note)