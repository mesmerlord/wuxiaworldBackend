from wuxiaworld.novels.models import Report
from wuxiaworld.novels.serializers import ReportSerializer
from rest_framework import viewsets
from wuxiaworld.novels.permissions import IsSuperUser, ReadOnly
from rest_framework import permissions

class ReportSerializerView(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsSuperUser, ]
        elif self.action == 'create':
            self.permission_classes = [permissions.AllowAny,]
        else:
            self.permission_classes = [ReadOnly,]
        return super(ReportSerializerView, self).get_permissions()