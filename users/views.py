from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

import random
import json




# Create your views here.

@never_cache
def UserSignUp(request):
    if request.method == 'POST':

        firstname = request.POST.get('firstName') 
        lastname = request.POST.get('lastName')
        username = request.POST.get('userName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        copassword = request.POST.get('coPassword')
 
        error_messages = []

        if firstname.isspace():
            error_messages.append('Firstname not be spaces')
        if lastname.isspace():
            error_messages.append('Lastname not be spaces')

        if User.objects.filter(username=username).exists():
            error_messages.append('Try another username')

        if User.objects.filter(email=email).exists():
            error_messages.append('account already exists in this email id')    

        try:
             validate_email(email)
        except:
            error_messages.append('Invalid email address')  

        if len(str(password)) < 8 :
            error_messages.append('Password must contains 8  characters long')  

        if password != copassword :
            error_messages.append('Password do not match')      


        if error_messages:
            for message in error_messages:
                messages.error(request,message)
            return  render(request, 'user_signup.html',{'first_name':firstname,'last_name': lastname, 'username':username,'email':email})          


        user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
        user.save()
        messages.success(request,'Regidtration completed Successfully') 
        return redirect('user_signin')
    
    return render(request,'user_signup.html')



def UserSignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            username = email 

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home or any other page
        else:
            messages.error(request, 'Invalid email or password')
              
    return render(request, 'user_signin.html')            
        
@login_required
def Home(request):
    return render(request, 'home.html')


def userLogout(request):
    logout(request)
    return redirect('user_signin')




# ------------------------------------------------------------------------------


def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)]) #gnerate an 6 digit OTP

def send_otp_email(email, otp):
    """Send OTP via email."""
    subject = 'Your Password Reset OTP'
    message = f'Your OTP is: {otp}\n\n This OTP will expire in 5 minutes.'
    try:
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False



def initiate_password_reset(request):
    """Start password reset process by sending OTP."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            # Verify user exists
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp = generate_otp()
            
            # Create OTP session data
            otp_data = {
                'otp': otp,
                'email': email,
                'created_at': timezone.now().isoformat(),
                'attempts': 0,
                'resend_count': 0
            }
            
            # Send OTP email
            if send_otp_email(email, otp):
                                                # Store OTP data in session
                request.session['password_reset_otp'] = json.dumps(otp_data)
                request.session.set_expiry(600)                              # 10 minutes session timeout
                
                messages.success(request, 'OTP sent successfully!')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
        
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return render(request, 'verify_email.html')


def verify_otp(request):
    """Verify the OTP entered by the user."""
    if request.method == 'POST':
        # Retrieve OTP data from session
        stored_otp_json = request.session.get('password_reset_otp')
        
        if not stored_otp_json:
            messages.error(request, 'OTP session expired. Please restart the process.')
            return redirect('initiate_password_reset')
        
        # Parse stored OTP data
        stored_otp_data = json.loads(stored_otp_json)
        
        # Check OTP attempts
        if stored_otp_data['attempts'] >= 3:
            del request.session['password_reset_otp']
            messages.error(request, 'Too many incorrect attempts. Please restart the process.')
            return redirect('initiate_password_reset')
        
        # Get current time and created time
        created_at = timezone.datetime.fromisoformat(stored_otp_data['created_at'])
        current_time = timezone.now()
        
        # Check OTP timeout (5 minutes)
        if (current_time - created_at).total_seconds() > 300:
            del request.session['password_reset_otp']
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('initiate_password_reset')
        
        # Verify OTP
        otp_entered = request.POST.get('otp')
        
        if otp_entered == stored_otp_data['otp']:
            # Reset session for password reset
            email = stored_otp_data['email']
            del request.session['password_reset_otp']
            
            # Set a new session for password reset
            request.session['password_reset_email'] = email
            request.session.set_expiry(600)  # 10 minutes
            
            messages.success(request, 'OTP verified successfully!')
            return redirect('reset_password')
        else:
            # Increment attempts
            stored_otp_data['attempts'] += 1
            request.session['password_reset_otp'] = json.dumps(stored_otp_data)
            
            messages.error(request, f'Invalid OTP. {3 - stored_otp_data["attempts"]} attempts remaining.')
    
    return render(request, 'verify_otp.html')


def resend_otp(request):
    """Resend OTP with rate limiting."""
    # Retrieve OTP data from session
    stored_otp_json = request.session.get('password_reset_otp')
    
    if not stored_otp_json:
        messages.error(request, 'No active OTP session. Please restart.')
        return redirect('initiate_password_reset')
    
    # Parse stored OTP data
    stored_otp_data = json.loads(stored_otp_json)
    
    # Check resend count (max 3 resends)
    if stored_otp_data.get('resend_count', 0) >= 3:
        del request.session['password_reset_otp']
        messages.error(request, 'Maximum resend attempts reached. Please restart.')
        return redirect('initiate_password_reset')
    
    # Generate new OTP
    new_otp = generate_otp()
    
    # Update OTP data
    stored_otp_data['otp'] = new_otp
    stored_otp_data['created_at'] = timezone.now().isoformat()
    stored_otp_data['attempts'] = 0
    stored_otp_data['resend_count'] = stored_otp_data.get('resend_count', 0) + 1
    
    # Send new OTP
    if send_otp_email(stored_otp_data['email'], new_otp):
        # Update session with new OTP data
        request.session['password_reset_otp'] = json.dumps(stored_otp_data)
        request.session.set_expiry(600)  # 10 minutes session timeout
        
        messages.success(request, 'New OTP sent successfully!')
    else:
        messages.error(request, 'Failed to send new OTP. Please try again.')
    
    return redirect('verify_otp')

def reset_password(request):
    """Reset password after successful OTP verification."""
    # Check if user reached this page through OTP verification
    if 'password_reset_email' not in request.session:
        messages.error(request, 'Invalid access. Please restart.')
        return redirect('initiate_password_reset')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html')
        
        try:
            email = request.session['password_reset_email']
            user = User.objects.get(email=email)
            
            # Set and save new password
            user.set_password(new_password)
            user.save()
            
            # Clear the session
            del request.session['password_reset_email']
            
            messages.success(request, 'Password reset successfully.')
            return redirect('user_signin')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    return render(request, 'reset_password.html')