from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 2
    max_page_size =10
    last_page_strings = "This is Last Page"
    invalid_page_message = "This is invalid Page"