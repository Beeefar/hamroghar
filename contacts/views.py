from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Contact
from django.core.mail import send_mail

def contact(request):
	if request.method == 'POST':
		listing_id = request.POST['listing_id']
		listing = request.POST['listing']
		name = request.POST['name']
		email = request.POST['listing_id']
		message = request.POST['listing_id']
		phone = request.POST['phone']
		user_id = request.POST['user_id']
		realtor_email = request.POST['listing_id']

		#if user already made an inquiry for same home
		if request.user.is_authenticated:
			user_id = request.user.id
			has_contacted = Contact.objects.all().filter(user_id=user_id,listing_id=listing_id)

			if has_contacted:
				messages.error(request, 'You have already made an enquiry for this listing')
				return redirect('/listings/'+listing_id)


		contact = Contact(listing=listing,listing_id=listing_id,name=name, email=email, message=message, phone=phone,user_id=user_id)

		contact.save()

		send_mail(
			'Property Listing Enquiry',
			'We have an enquiry for '+listing+ '.Sign in to admin panel for more info',
		 	'agcy7320@gmail.com',
		  	[realtor_email,'c.iitaman@gmail.com'],
		  	fail_silently=False
		  	)
	    
		messages.success(request,'You request has been successfully submitted to realtor')

		return redirect('/listings/'+listing_id)