from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from celery.result import AsyncResult

class APITaskStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        result = AsyncResult(task_id)
        
        status = 'pending'
        if result.ready():
            if result.successful():
                status = 'complete'
            else:
                status = 'failed'
        
        response_data = {
            'id': task_id,
            'status': status,
        }
        
        if status == 'complete':
            response_data['result'] = result.result
        elif status == 'failed':
            response_data['error'] = str(result.result)
        
        return Response(response_data, status=status.HTTP_200_OK)

