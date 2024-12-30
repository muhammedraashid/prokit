from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from .models import Address
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count

import requests
import phonenumbers
from phonenumbers import geocoder

# Create your views here.


def get_location(pincode):
    api_key = '73515090-a344-11ef-a6ab-69a0d479c7d0'
    url = 'https://app.zipcodebase.com/api/v1/search'
    params = {'codes': pincode}
    headers = {'apikey': api_key}

    try:    
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            if 'results' in data and pincode in data['results']:
                location = data['results'][pincode][0]
                country = location.get('country_code', None)
                state = location.get('state', None)
                city = location.get('city', None)

                return country, state, city
        return None, None, None

    except requests.exceptions.RequestException as e:
        return None, None, None
    
@login_required
def add_address(request):
    if request.method == "POST":
        address_type = request.POST.get('address_type')
        name = request.POST.get('name')
        street_address = request.POST.get('street_address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        is_default = request.POST.get('is_default') == 'on' 

        if not (address_type and name and street_address and pincode and phone and email):
            messages.error(request, "All fields are Required")
            return redirect('add_address')
        
        country, state, city = get_location(pincode)

        if is_default:
           Address.objects.filter(user=request.user).update(is_default=False) 

        Address.objects.create(
            user = request.user,
            address_type = address_type,
            name = name,
            country = country,
            state = state,
            city = city,
            street_address = street_address,
            pincode = pincode,
            phone = phone,
            email = email,
            is_default = is_default
        )
        messages.success(request, f"Address {address_type} added succesfully")
    return redirect('user_addresses')
    

@login_required       
def UserAddresses(request):
    user =  request.user
    addresses = user.addresses.filter(is_deleted=False)

    context = {
        'user':user,
        'addresses':addresses
    }
    return render(request, 'addresses.html',context)

def update_address(request,address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == "POST":
        address_type = request.POST.get('address_type')
        name = request.POST.get('name')
        street_address = request.POST.get('street_address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        is_default = request.POST.get('is_default') == 'on' 

        if not (address_type or name or street_address or pincode or phone or email):
            messages.error(request, "All fields are Required")
            return redirect('add_address')
        
        country, state, city = get_location(pincode)

        if is_default:
           Address.objects.filter(user=request.user).update(is_default=False) 
        
        address.address_type = address_type
        address.name = name
        address.street_address = street_address
        address.country = country
        address.state = state
        address.city = city
        address.pincode = pincode
        address.phone = phone
        address.email = email
        address.is_default = is_default
        address.save()
        messages.success(request,f'{address.address_type} address successfully upadated')
    return redirect("user_addresses")


@login_required
def delete_address(request,address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address.soft_delete()
        messages.success(request,f'{address.address_type} address removed succesfully')
        
    return redirect('user_addresses')

