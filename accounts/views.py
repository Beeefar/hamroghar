from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from contacts.models import Contact

def register(request):
	if request.method == 'POST':
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password2 = request.POST['password2']

		#Check if passwords match
		if password == password2:
			#Check Username
			if User.objects.filter(username=username).exists():
				messages.error(request, 'Username already exists!')
				return redirect('register')
			else:
				#Check email
				if User.objects.filter(email=email).exists():
					messages.error(request, 'Email entered is already registered!')
					return redirect('register')
				else:
					#Now create user as all is fine
					user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,password=password)
					
					#if want login directly after register
					#auth.login(request,user)
					#messages.success(request,'you are now logged in!')
					#return redirect('index')

					#if want to just register and say user to login manually
					user.save()
					messages.success(request,'You are now registered!')
					return redirect('login')
		else:
			messages.error(request, 'Passwords do not match!')
			return redirect('register')

	else:
		return render(request, 'accounts/register.html')



def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username,password=password) 

		if user is not None:
			auth.login(request, user)
			messages.success(request, 'You are now logged in!')
			return redirect('dashboard')
		else:
			messages.error(request,'Invalid Credentials')
			return redirect('login')
	else:
		return render(request, 'accounts/login.html')



def logout(request):
	if request.method == 'POST':
		auth.logout(request)
		messages.success(request, 'You are now logged out')
		return redirect('index')



def dashboard(request):
	#request.user.id will give the id of the current user logged in
	user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)

	context = {
		'contacts':user_contacts
	}
	return render(request, 'accounts/dashboard.html',context)