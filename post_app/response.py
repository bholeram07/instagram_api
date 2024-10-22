from rest_framework.response import Response
from rest_framework import status
def response(status,data=None,message=None,error=None):
    if data:
       return Response({
        "message" : message,
        "data" : data,
    },status = status) 
    if error:
       return Response({
           "error" : error,
            
       },status= status)