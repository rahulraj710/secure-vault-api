from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.serializers import RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "account created"}, status=201)
        return Response(serializer.errors, status=400)
