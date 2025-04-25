from django.conf import settings

class XFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the request path matches the editor path
        if request.path.startswith('/mycontent/') and '/editor' in request.path:
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        return response 