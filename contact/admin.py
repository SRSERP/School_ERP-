from django.contrib import admin
from .models import Contact




@admin.register(Contact)
class ProductAdmin(admin.ModelAdmin):
   
    list_display = [field.name for field in Contact._meta.fields]