# from django.shortcuts import render, redirect
# from contact.models import Contact
# from django.contrib import messages

# def contact_view(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         print(name)
#         email = request.POST.get('email')
#         print(name)
#         contact_number = request.POST.get('contact_number')
#         print(name)
#         company = request.POST.get('company')
#         print(name)
#         country = request.POST.get('country')
#         print(name)
#         heard_from = request.POST.get('heard_from')
#         print(name)
#         message = request.POST.get('message')
#         print(name)

#         # Save to database
#         Contact.objects.create(
#             name=name,
#             email=email,
#             contact_number=contact_number,
#             company=company,
#             country=country,
#             heard_from=heard_from,
#             message=message,
#         )

#         messages.success(request, 'Your message has been submitted.')
#         return redirect('contact')

#     return render(request, 'Contact.html')
