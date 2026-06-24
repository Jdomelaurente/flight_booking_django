from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from ..models import PasswordResetOTP, PasswordSetupToken
import random
import uuid

class RequestOTPView(APIView):
    authentication_classes = [] # No auth required
    permission_classes = [] # Allow anyone

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # We return success to prevent email enumeration
            return Response({'message': 'If an account exists, an OTP has been sent.'})

        # Generate 6-digit code
        otp_code = ''.join(random.choices('0123456789', k=6))
        
        # Save to DB
        PasswordResetOTP.objects.create(user=user, otp_code=otp_code)

        # Send Email
        subject = 'TourSim - Your Password Reset Code'
        context = {
            'name': user.first_name or user.username,
            'otp_code': otp_code,
            'year': timezone.now().year
        }
        html_message = render_to_string('emails/password_reset_otp.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )

        return Response({'message': 'OTP sent successfully'})

class VerifyOTPAndResetView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp_code, new_password]):
            return Response({'error': 'Email, OTP, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(user=user, otp_code=otp_code).first()

            if otp_record and otp_record.is_valid():
                # Success! Change password
                user.set_password(new_password)
                user.save()
                
                # Mark as used
                otp_record.is_used = True
                otp_record.save()
                
                return Response({'message': 'Password reset successful'})
            else:
                return Response({'error': 'Invalid or expired OTP code'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class SetPasswordWithTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({'error': 'Token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record = PasswordSetupToken.objects.filter(token=token, is_used=False).first()
            if not record or not record.is_valid():
                return Response({'error': 'Invalid or expired setup link. Please contact your administrator.'}, status=status.HTTP_400_BAD_REQUEST)

            user = record.user
            user.set_password(new_password)
            user.save()

            record.is_used = True
            record.save()

            return Response({'message': 'Password set successfully! You can now log in.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
