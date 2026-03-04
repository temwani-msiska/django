from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class PlaygroundRunView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '')
        language = request.data.get('language', 'javascript')
        output = 'Hello World!' if code else 'No code provided.'
        return Response({'output': output, 'error': None, 'language': language})
