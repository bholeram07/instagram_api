from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc , context):
    response = exception_handler(exc,context)
    if response is not None:
        return Response({
           'error':{
                'status_code' : response.status_code,
                 'message': response.data.get('detail', 'Something went wrong'),
            }
        },status= response.status_code)
    
    return Response({
        'error': {
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Internal server error',
        }
    })