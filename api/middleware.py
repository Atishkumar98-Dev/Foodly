# yourproject/middleware.py
import re
from django.http import JsonResponse
from django.conf import settings

API_PATH_PREFIX = re.compile(r"^/api(?:/|$)")  # matches /api and /api/...

class RequireApiTokenMiddleware:
    """
    For any path starting with /api, require a token in one of:
      - Authorization: Token <value>
      - Authorization: Bearer <value>
      - X-API-Key: <value>

    Returns 401 JSON on failure.
    Allows CORS preflight (OPTIONS) to pass without token.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Read once; set this via environment variable in production.
        self.expected_token = getattr(settings, "API_SECRET_TOKEN", None)

    def __call__(self, request):
        path = request.path

        # Only guard /api...
        if API_PATH_PREFIX.match(path):
            # Let CORS preflight through so browsers can ask permission
            if request.method == "OPTIONS":
                return self._unauthorized_preflight_ok()

            token = self._extract_token(request)

            if not self.expected_token or token != self.expected_token:
                return JsonResponse(
                    {"detail": "Missing or invalid API token."},
                    status=401
                )

        return self.get_response(request)

    def _extract_token(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Token "):
            return auth.split(" ", 1)[1].strip()
        if auth.startswith("Bearer "):
            return auth.split(" ", 1)[1].strip()
        x_api = request.META.get("HTTP_X_API_KEY")
        if x_api:
            return x_api.strip()
        return None

    def _unauthorized_preflight_ok(self):
        # Minimal OK for preflight; adjust headers if you use django-cors-headers
        return JsonResponse({"detail": "Preflight OK"}, status=200)
