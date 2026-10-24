from django.http import HttpResponse
from django.shortcuts import render
from contact.models import Contact

def index_view(request):
     return render (request , 'index.html')


def header_view(request):
     return render(request, 'header.html')

def About_view(request):
     return render (request , 'About.html')



def Service_view(request):
     return render (request , 'services.html')

def Seo_view(request):
     return render (request , 'seo.html')

def Web_design_view(request):
     return render (request , 'web_designing.html')

def Why_Choose_view(request):
     return render (request , 'why_choose.html')
def Portfolio_view(request):
     return render (request , 'Portfolio.html')

# def Contact_view(request):
#      return render (request , 'Contact.html')



# def Web_hoisting(request):
#      return render (request , 'web_hoisting.html')     

def demo_view(request):
     return render (request , 'Demo.html')


from django.shortcuts import render, redirect
from contact.models import Contact
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging

def Contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(name)
        email = request.POST.get('email')
        print(email)
        contact_number = request.POST.get('contact_number')
        print(contact_number)
        company = request.POST.get('company')
        print(company)
        country = request.POST.get('country')
        print(country)
        heard_from = request.POST.get('heard_from')
        print(heard_from)
        message = request.POST.get('message')
        print(message)

        # Save to database
        Contact.objects.create(
            name=name,
            email=email,
            contact_number=contact_number,
            company=company,
            country=country,
            heard_from=heard_from,
            message=message,
        )
        
        try:
            send_mail(
                subject="Thank You for Contacting Us",
                message=f"Hi {name},\n\nThank you for reaching out. We have received your message and will get back to you shortly.\n\nRegards,\nTeam",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            print("send mail")
        except Exception as e:
             print(f'{e=}')
             pass #  (f"Error sending confirmation email: {e}")

        messages.success(request, 'Your message has been submitted.')
        return redirect('Contact')

    return render(request, 'Contact.html')
