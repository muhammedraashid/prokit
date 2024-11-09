from typing import Any
from django.shortcuts import redirect

class RedirectHomeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    
    def __call__(self, request):
        if request.user.is_authenticated and request.path in ['/', '/signin/', '/signup/']:
            return redirect('home')  
        response = self.get_response(request)
        
        return response
    
   
    