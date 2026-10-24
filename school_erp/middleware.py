from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationRequiredMiddleware:
    """
    Middleware that enforces login for all application views.
    - If unauthenticated user accesses '/' (root), redirects directly to /login/
    - If unauthenticated user accesses any protected page (or session expired), redirects to /login/?next=<path>
    - Allows public URLs like /login/, /logout/, /static/, /media/, /admin/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        
        # Public path prefixes that do not require an active login session
        public_prefixes = (
            '/login/',
            '/logout/',
            '/static/',
            '/media/',
            '/admin/',  # Django admin handles its own authentication
            '/slip/',   # Public digital slips for parents (receipts, report cards, ID cards)
        )
        
        is_public = any(path.startswith(prefix) for prefix in public_prefixes)
        
        if not is_public and not request.user.is_authenticated:
            # Session expired or not logged in
            if path == '/':
                return redirect('user_login')
            return redirect(f"{reverse('user_login')}?next={path}")
            
        return self.get_response(request)
