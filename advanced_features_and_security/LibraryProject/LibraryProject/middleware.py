from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class CSPMiddleware(MiddlewareMixin):
    """Attach a basic Content-Security-Policy header for XSS mitigation."""

    def process_response(self, request, response):
        csp = getattr(settings, 'CONTENT_SECURITY_POLICY', None)
        if csp:
            response['Content-Security-Policy'] = csp
        # Provide XSS filter header for older browsers if enabled
        if getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False):
            response['X-XSS-Protection'] = '1; mode=block'
        return response
