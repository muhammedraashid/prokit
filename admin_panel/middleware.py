from typing import Any
from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    
    def __call__(self, request):
        if not request.user.is_superuser and request.path == '/admin/dashboard/':
            return redirect('admin_signin')
        response = self.get_response(request)
        return response
   
    