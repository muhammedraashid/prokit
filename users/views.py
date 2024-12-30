from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, EmailVerification 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from products.models import Product, Variant
from categories.models import Category
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
<<<<<<< HEAD
from django.db.models import Max,Prefetch
from django.utils.crypto import get_random_string
=======
from django.db.models import Max, Prefetch
>>>>>>> d756ca4a21213be48b520aeb4ac8d006218a36e3

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

        if not firstname.strip():
            error_messages.append('First name cannot be empty or spaces.')
        if not lastname.strip():
            error_messages.append('Last name cannot be empty or spaces.')

        if User.objects.filter(username=username).exists():
            error_messages.append('Try another username')

        if User.objects.filter(email=email).exists():
            error_messages.append('Account already exists in this email id')    

        try:
            validate_email(email)
        except ValidationError:
            error_messages.append('Invalid email address') 
  

        if len(str(password)) < 8 :
            error_messages.append('Password must contains 8  characters long')  

        if password != copassword :
            error_messages.append("Password doesn't matching")      


        if error_messages:
            for message in error_messages:
                messages.error(request,message)
            return  render(request, 'user_signup.html',{'first_name':firstname,'last_name': lastname, 'username':username,'email':email})          


        user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
        user.is_active = False
        user.save()
        messages.success(request,'Registration successful! Please check your email to verify your account.') 
        return redirect('user_signin')
    
    return render(request,'user_signup.html')

def verify_email(request, token):
    verification = get_object_or_404(EmailVerification, token=token)

    if verification.user.is_active :
        messages.info(request,"Your email alredy verified")
    else:
        verification.user.is_active = True
        verification.user.save()
        verification.delete()
        messages.success(request, "Your email verified successfully! Now you can sign in ")    
    return redirect('user_signin')

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
            return redirect('home') 
        else:
            messages.error(request, 'Invalid email or password')
              
<<<<<<< HEAD
    return render(request, 'user_signin.html')  
         
=======
    return render(request, 'user_signin.html')           
>>>>>>> d756ca4a21213be48b520aeb4ac8d006218a36e3
@login_required
def Home(request, category_id=None):
    categories = Category.objects.filter(is_listed=True)[:4]
<<<<<<< HEAD
    category = None
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(is_listed=True,category=category).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))).order_by('name')             
        variants = Variant.objects.all().order_by('-created_at')[:12]
    else:    
        products = Product.objects.filter(is_listed=True).prefetch_related(
                    Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))).order_by('name')             
        variants = Variant.objects.all().order_by('-created_at')[:12]
        
=======
    products = Product.objects.filter(is_listed=True).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))).order_by('name')             

    variants = Variant.objects.all().order_by('-created_at')[:12]
>>>>>>> d756ca4a21213be48b520aeb4ac8d006218a36e3
    context = {
        "products":products,
        "variants":variants,
        "categories":categories,
        "selected_category":category 
    }

    return render(request, 'home.html',context)


def userLogout(request):
    logout(request)
    return redirect('user_signin')




# ------------------------------------------------------------------------------


def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)]) #gnerate an 6 digit OTP

def send_otp_email(email, otp):
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
        return False



def initiate_password_reset(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try: 
            user = User.objects.get(email=email) # check user exists        
            otp = generate_otp() # generate otp
                  
            otp_data = {   
                'otp': otp,
                'email': email,
                'created_at': timezone.now().isoformat(),
                'attempts': 0,
                'resend_count': 0
            }
            
            # Send OTP email
            if send_otp_email(email, otp):
                                               
                request.session['password_reset_otp'] = json.dumps(otp_data)  # create otp session
                request.session.set_expiry(600)      # after 10 minutes session timeout
                
                messages.success(request, 'OTP sent successfully!')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
        
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return render(request, 'verify_email.html')


def verify_otp(request):
   
    if request.method == 'POST':
        
        stored_otp_json = request.session.get('password_reset_otp') 
        
        if not stored_otp_json:
            messages.error(request, 'OTP session expired. Please restart the process.')
            return redirect('initiate_password_reset')
        
      
        stored_otp_data = json.loads(stored_otp_json)
        
       
        if stored_otp_data['attempts'] >= 3:
            del request.session['password_reset_otp']
            messages.error(request, 'Too many incorrect attempts. Please restart the process.')
            return redirect('initiate_password_reset')
        
        
        created_at = timezone.datetime.fromisoformat(stored_otp_data['created_at'])
        current_time = timezone.now()
        
        
        if (current_time - created_at).total_seconds() > 300: # check otp timeout - 5 minutes
            del request.session['password_reset_otp']
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('initiate_password_reset')
        
       
        otp_entered = request.POST.get('otp') # get the otp from user
        
        if otp_entered == stored_otp_data['otp']:
            email = stored_otp_data['email']
            del request.session['password_reset_otp']
            
            
            request.session['password_reset_email'] = email    # creating new session for reset password
            request.session.set_expiry(600) 
            
            messages.success(request, 'OTP verified successfully!')
            return redirect('reset_password')
        else:
            

            stored_otp_data['attempts'] += 1
            request.session['password_reset_otp'] = json.dumps(stored_otp_data)
            
            messages.error(request, f'Invalid OTP. {3 - stored_otp_data["attempts"]} attempts remaining.')
    
    return render(request, 'verify_otp.html')


def resend_otp(request):
   
    stored_otp_json = request.session.get('password_reset_otp')
    
    if not stored_otp_json:
        messages.error(request, 'No active OTP session. Please restart.')
        return redirect('initiate_password_reset')
    
   
    stored_otp_data = json.loads(stored_otp_json)
    
    #
    if stored_otp_data.get('resend_count', 0) >= 3: # check resend attempts 
        del request.session['password_reset_otp']
        messages.error(request, 'Maximum resend attempts reached. Please restart.')
        return redirect('initiate_password_reset')
    
    
    new_otp = generate_otp() # generatenew otp
    
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

# ----------------------------------------------------------------------------------------------
#   user-profile
# ---------------------------------------------------------------------------------------------
@login_required
def UserAccount(request):
    user = request.user
    total_orders = user.orders.all().count()
    total_wishlist = user.wishlist.items.all().count()
    total_cart = user.cart.cartitems.all().count()
    # total_reviews = user.reviews.all().count()

    context = {
        "total_orders":total_orders,
        "total_wishlist":total_wishlist,
        "total_cart":total_cart,
        # "total_reviews":total_reviews
    }
    return render(request, 'account.html',context)

@login_required
def UserProfile(request):
    user = request.user
    user_id = user.id
    if request.method == "POST":
        firstname = request.POST.get('first_name') 
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        copassword = request.POST.get('co_password')
 
        error_messages = []

        if firstname.isspace():
            error_messages.append('Firstname not be spaces')
        if lastname.isspace():
            error_messages.append('Lastname not be spaces')

        if User.objects.filter(username=username).exclude(id=user_id).exists():
            error_messages.append('Try another username')
        
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            error_messages.append('account already exists in this email id')    

        try:
             validate_email(email)
        except:
            error_messages.append('Invalid email address')  
       
        if password :
            if len(str(password)) < 8 :
                error_messages.append('Password must contains 8  characters long')  

            if password != copassword :
                error_messages.append('Password not matching !')      


        if error_messages:
            for message in error_messages:
                messages.error(request,message)
                
            return  render(request, 'profile.html',{'first_name':firstname,'last_name': lastname, 'username':username,'email':email})          
        
        verification_code = get_random_string(6, allowed_chars='0123456789')
        subject = "Verify Your Email Address"
        message = f"Hi {firstname},\n\n Please use the following code to verify your email address : \n\n {verification_code}\n\n Thank you !"
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, [email])
            messages.info(request, f"A verification code has been sent to {email}. Please check your inbox.")
        except Exception as e:
            messages.error(request, "Failed to send verification email. Please try again later.")
            return render(request, 'profile.html', {'user': user})
         
        user.username = username
        user.first_name = firstname
        user.last_name = lastname
        if password:
            user.set_password(password)
            user.save()
            messages.success(request,'Password succesfully reseted')
        if phone :
            user.profile.phone_number = phone
            user.profile.save()    
            messages.success(request, 'Phone Number Updated')
        user.save()
        
        messages.success(request,'Profile Updated Successfully') 
        return render(request,'profile.html',{"user":user})

    context ={
        'user':user
    }
    return render(request,'profile.html',context)