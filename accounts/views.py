from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import RegistrationSerializer, LoginSerializer
from accounts.models import User

class RegistrationView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "account created"}, status=201)
        return Response(serializer.errors, status=400)
    

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            user = User.objects.get(email = serializer.validated_data['email'])
        except User.DoesNotExist:
            # user does not exist
            return Response({'error': 'Invalid credentials'}, status=401)
        
        if user.is_locked:
            if timezone.now() - user.locked_at > settings.LOCKOUT_DURATION:
                user.is_locked = False
                user.failed_login_attempts = 0
                user.locked_at = None
                user.save(update_fields=['is_locked', 'locked_at', 'failed_login_attempts'])
            else: 
                # user locked
                return Response({'error': 'Account temporarily locked'}, status=403)
        
        if not user.check_password(serializer.validated_data['password']):
            # invalid credentials
            failed_login_attempts = user.failed_login_attempts + 1
            if failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.is_locked = True
                user.locked_at = timezone.now()
                user.failed_login_attempts = failed_login_attempts
                user.save(update_fields=['is_locked', 'locked_at', 'failed_login_attempts'])
            return Response({'error': 'Invalid credentials'}, status=401)
        
        # successful login
        user.failed_login_attempts = 0
        user.save(update_fields=['failed_login_attempts'])
        
        refresh = RefreshToken.for_user(user)
        return Response({"access_token": str(refresh.access_token),"refresh":str(refresh)}, status=200)

