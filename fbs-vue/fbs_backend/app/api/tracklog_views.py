from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
import csv
from django.http import HttpResponse
from ..models import TrackLog
from ..serializers import TrackLogSerializer

class TrackLogViewSet(viewsets.ModelViewSet):
    queryset = TrackLog.objects.all().order_by('-timestamp')
    serializer_class = TrackLogSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'action']
    ordering_fields = ['timestamp', 'id']

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        """Purge all audit logs"""
        count = TrackLog.objects.count()
        TrackLog.objects.all().delete()
        return Response(
            {'message': f'Successfully cleared {count} audit records.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='export')
    def export_csv(self, request):
        """Export logs to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Action', 'Timestamp'])
        
        logs = self.get_queryset()
        for log in logs:
            writer.writerow([
                log.id,
                log.user.username if log.user else 'System',
                log.action,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
            
        return response
