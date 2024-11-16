import uuid
from django.http import JsonResponse
from django.urls import resolve


class UUIDValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.check_uuid_in_url(request)
        if response:
            return response
        return self.get_response(request)

    def check_uuid_in_url(self, request):
        try:
            resolved = resolve(request.path_info)
            print(f"Resolved view: {resolved}")
            url_params = resolved.kwargs 
            print(f"URL Params: {url_params}")
        except Exception as e:
            print(f"Exception resolving path: {e}")
            return None 

        for param, value in url_params.items():
            if not self.is_valid_uuid(value):
                print(f"Invalid UUID: {value} for param {param}")
                return JsonResponse(
                    {"detail": f"The provided {param} UUID is not in a valid format."},
                    status=400
                )
        return None

    def is_valid_uuid(self, value):
        print(f"Validating UUID: {value}")
        if isinstance(value, str):
            try:
                uuid_obj = uuid.UUID(value)
                is_valid = str(uuid_obj) == value
                print(f"Validation result for {value}: {is_valid}")
                return is_valid
            except ValueError:
                print(f"Validation failed for {value}")
                return False
        print(f"Value {value} is not a string")
        return False
