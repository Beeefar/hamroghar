from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from django.core.mail import send_mail

def contact(request):
    # Handle GET requests - redirect to homepage or show a simple message
    if request.method != 'POST':
        messages.info(request, 'Please submit the contact form properly')
        return redirect('index')  # Assuming 'index' is the name of your homepage URL

    # Handle POST requests
    try:
        listing_id = request.POST['listing_id']
        listing = request.POST['listing']
        name = request.POST['name']
        email = request.POST['email']  # Fixed from listing_id to email
        message = request.POST['message']  # Fixed from listing_id to message
        phone = request.POST['phone']
        user_id = request.POST['user_id']
        realtor_email = request.POST['realtor_email']  # Fixed from listing_id to realtor_email

        # Check if user already made inquiry for this listing
        if request.user.is_authenticated:
            user_id = request.user.id
            has_contacted = Contact.objects.filter(user_id=user_id, listing_id=listing_id).exists()
            
            if has_contacted:
                messages.error(request, 'You have already made an enquiry for this listing')
                return redirect('/listings/' + listing_id)

        # Create and save contact
        contact = Contact(
            listing=listing,
            listing_id=listing_id,
            name=name,
            email=email,
            message=message,
            phone=phone,
            user_id=user_id
        )
        contact.save()

        # Send email
        send_mail(
            'Property Listing Enquiry',
            f'We have an enquiry for {listing}. Sign in to admin panel for more info',
            'helloofrns@gmail.com',
            [realtor_email, "helloofrns@gmail.com"],
            fail_silently=False
        )
        
        messages.success(request, 'Your request has been successfully submitted to realtor')
        return redirect('/listings/' + listing_id)

    except KeyError as e:
        messages.error(request, f'Missing required field: {e}')
        return redirect('/listings/' + request.POST.get('listing_id', ''))
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return redirect('index')