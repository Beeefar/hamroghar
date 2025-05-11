from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from .validators import validatePassword
from django.utils import timezone   
from django.http import HttpResponseServerError
from .models import UserLogin
from contacts.models import Contact
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

# Create your views here.
def register(request):
    if request.method == "POST":
        # Register User
        
        # Get form values
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Check if passwords meet the basic requirements of containing at least:
            # 1. 1 Special Character (!@#$%^&*_)
            # 2. 1 Uppercase Character
            # 3. 1 Lowercase Character
            # 4. At least 8 characters long
        if validatePassword(request,password) == False or validatePassword(request,password2) == False:
            return redirect('register')

        # Validate the email
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            # Handle the validation error
            messages.error(request,'Please enter a valid email!')
            return redirect('register')
        
        # Check if passwords match
        if password == password2:
            # check if the username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is taken!')
                return redirect('register')
            # check if the email exists
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email is taken!')
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username,password=password, email = email, first_name = first_name, last_name = last_name)
                    user.save()
                    messages.success(request,'You are now registered and can log in!')
                    return redirect('login')
        else:
            messages.error(request,"Passwords do not match!")
            return redirect('register')
                
    else:
        return render(request,'accounts/register.html')

def login(request):
    # If POST request
    if request.method == "POST":
        # Get username and password from request
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if user exists
        user = auth.authenticate(username=username, password=password)

        # If user matched
        if user is not None:
            # If user had previous wrong password attempts, reset counter
            user_login = UserLogin.objects.filter(user=user).last()
            if user_login:
                # Check if user is still timed out
                if user_login.wrong_password_timeout is not None and user_login.wrong_password_timeout > timezone.now():
                    remaining_time = user_login.wrong_password_timeout - timezone.now()
                    remaining_time_minutes, remaining_time_seconds = divmod(remaining_time.seconds, 60)
                    remaining_time_str = f"{remaining_time_minutes} minutes and {remaining_time_seconds} seconds"
                    context = {'remaining_time': remaining_time_str}
                    content = render(request, 'accounts/lockedOut.html', context=context)
                    return HttpResponseServerError(content)
                else:
                    user_login.wrong_password_count = 0
                    user_login.wrong_password_timeout = None
                    user_login.save()
            auth.login(request, user)
            return redirect('dashboard')

        # If failed to match
        else:
            # Increment wrong password counter in session
            user_login = UserLogin.objects.filter(user__username=username).last()

            if user_login:
                if user_login.wrong_password_count < 3:
                    user_login.wrong_password_count += 1
                user_login.save()
            else:
                # If there is such a user within the database, we create a UserLogin object for him, to track the wrong-password-count
                try:
                    user_login = UserLogin.objects.create(user=User.objects.get(username=username), wrong_password_count=1)
                # If there is no such user, we show an error message, and redirect him to the register page
                except User.DoesNotExist:
                    messages.error(request,"Unregistered Account! Register with PropertyIQ instead?")
                    return redirect('register')
            
            # only show message if they still have attempts left
            if user_login.wrong_password_count < 3:
                messages.error(request, f"Invalid credentials! Try again! You have {3 - user_login.wrong_password_count} attempts left.")

            # Check if user has exceeded max number of attempts
            if user_login.wrong_password_count >= 3:
                # Set timeout if it hasn't already been set
                if user_login.wrong_password_timeout is None:
                    user_login.wrong_password_timeout = timezone.now() + timezone.timedelta(hours=1)
                    user_login.save()
                    remaining_time = user_login.wrong_password_timeout - timezone.now()
                    remaining_time_minutes, remaining_time_seconds = divmod(remaining_time.seconds, 60)
                    remaining_time_str = f"{remaining_time_minutes} minutes and {remaining_time_seconds} seconds"
                    context = {'remaining_time': remaining_time_str}
                    content = render(request, 'accounts/lockedOut.html', context=context)
                    return HttpResponseServerError(content)
                    # return HttpResponseServerError(f"You have been timed out for {remaining_time_str}. Please try again later.")

                # Check if user is still timed out
                if user_login.wrong_password_timeout > timezone.now():
                    remaining_time = user_login.wrong_password_timeout - timezone.now()
                    remaining_time_minutes, remaining_time_seconds = divmod(remaining_time.seconds, 60)
                    remaining_time_str = f"{remaining_time_minutes} minutes and {remaining_time_seconds} seconds"
                    context = {'remaining_time': remaining_time_str}
                    content = render(request, 'accounts/lockedOut.html', context=context)
                    return HttpResponseServerError(content)
                    # return HttpResponseServerError(f"You have been timed out for {remaining_time_str}. Please try again later.")


                else:
                    # Reset counter and timeout if remaining time is zero or less than zero
                    # Reset count to 1, because if reached here, means they already failed once. hence, we set it to 1 instead of 0.
                    user_login.wrong_password_count = 1
                    user_login.wrong_password_timeout = None
                    user_login.save()
                    messages.error(request, f"Invalid credentials! Try again! You have {3 - user_login.wrong_password_count} attempts left.")
                
            return render(request, 'accounts/login.html')

    # If GET request
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.method == "POST":
        auth.logout(request)
    return redirect('index')



def dashboard(request):
	#request.user.id will give the id of the current user logged in
	user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)

	context = {
		'contacts':user_contacts
	}
	return render(request, 'accounts/dashboard.html',context)

def update(request):
    id = request.user.id
    user = User.objects.get(pk=id)
    if request.method == "POST":
        # Update User Account
        # Get form values
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check if passwords meet the basic requirements of containing at least:
            # 1. 1 Special Character (!@#$%^&*_)
            # 2. 1 Uppercase Character
            # 3. 1 Lowercase Character
            # 4. At least 8 characters long
        if validatePassword(request,password) == False or validatePassword(request,password2) == False:
            return redirect('update')
        # Validate the email
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            # Handle the validation error
            messages.error(request,'Please enter a valid email!')
            return redirect('register')
        if password == password2:
            # check if the username exists
            if username != user.username and User.objects.filter(username=username).exists():
                messages.error(request, 'Username is taken!')
                return redirect('update')
            # check if the email exists
            else:
                if email != user.email and User.objects.filter(email=email).exists():
                    messages.error(request, 'Email is taken!')
                    return redirect('update')
                else:
                    validator = EmailValidator()
                    try:
                        validator(email)
                    except ValidationError:
                        # Handle the validation error
                        messages.error(request,'Please enter a valid email!')
                        return redirect('update')
                    
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.username = username
                    user.password = make_password(password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request,"Account details successfully updated!")
                    return redirect('dashboard')

        else:
            messages.error(request,"Passwords do not match!")
            return redirect('update')
                
    else:
        context = {
            'user' : request.user
        }
        return render(request,'accounts/update.html', context)
  