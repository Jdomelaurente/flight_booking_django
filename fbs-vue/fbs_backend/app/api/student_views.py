from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import Students, PasswordSetupToken
from ..serializers import StudentsSerializer
from ..pagination import OptionalPagination
import random

from django.http import HttpResponse
import csv
from rest_framework.decorators import action
from rest_framework.response import Response

class StudentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student information.
    """
    queryset = Students.objects.all().order_by('id')
    serializer_class = StudentsSerializer
    permission_classes = [AllowAny]
    pagination_class = OptionalPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        gender = self.request.query_params.get('gender')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_number__icontains=search) |
                Q(email__icontains=search)
            )
            
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset

    def perform_destroy(self, instance):
        if instance.user:
            instance.user.delete()
        else:
            instance.delete()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        male = queryset.filter(gender__in=['mr', 'male']).count()
        female = queryset.filter(gender__in=['mrs', 'female']).count()
        other = total - (male + female)
        return Response({
            'total': total,
            'male': male,
            'female': female,
            'other': other
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['username', 'student_number', 'first_name', 'mi', 'last_name', 'email', 'phone', 'course', 'year_level', 'gender'])
        
        students = self.get_queryset()
        for s in students:
            writer.writerow([
                s.user.username if s.user else '',
                s.student_number,
                s.first_name,
                s.mi or '',
                s.last_name,
                s.email,
                s.phone_number,
                s.course,
                s.year_level,
                s.gender
            ])
            
        return response

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        try:
            student = self.get_object()
            if not student.user:
                return Response({'error': 'This student is not linked to a user account.'}, status=status.HTTP_400_BAD_REQUEST)

            user = student.user
            user.set_unusable_password()
            user.save()

            import uuid
            token = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
            PasswordSetupToken.objects.create(user=user, token=token)

            setup_url = f"{settings.FRONTEND_URL}/set-password?token={token}"

            context = {
                'name': student.first_name or user.username,
                'setup_url': setup_url,
                'student_number': student.student_number,
                'username': user.username,
                'year': timezone.now().year
            }
            html_message = render_to_string('emails/welcome_student.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                'CTHM FBS - Password Reset Instructions',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({'message': 'Password has been reset. An email has been sent to the student with instructions.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
