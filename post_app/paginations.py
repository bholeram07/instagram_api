from rest_framework.response import Response


class CustomPagination:
    def __init__(self, request, queryset, page_size=5):
        self.request = request
        self.queryset = queryset
        self.page_size = page_size
        self.page_number = self.get_page_number()
        self.total_records = self.queryset.count()
        self.total_pages = (self.total_records // self.page_size) + (
            1 if self.total_records % self.page_size > 0 else 0
        )
        self.paginated_data = self.get_paginated_data()

    def get_page_number(self):
        try:
            return int(self.request.query_params.get("page", 1))
        except ValueError:
            return 1

    def get_paginated_data(self):
        start_index = (self.page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        return list(self.queryset.all()[start_index:end_index])

    def get_paginated_response(self, data):
        return Response(
            {
                "total_records": self.total_records,
                "total_pages": self.total_pages,
                "current_page": self.page_number,
                "page_size": self.page_size,
                "results": data,
            }
        )
