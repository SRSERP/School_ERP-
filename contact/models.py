from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20,null= True, blank=True)
    company = models.CharField(max_length=100,null= True, blank=True)
    country = models.CharField(max_length=100,null= True, blank=True)
    heard_from = models.CharField(max_length=150,null= True, blank=True)
    message = models.TextField( max_length=500, null= True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null= True )

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
