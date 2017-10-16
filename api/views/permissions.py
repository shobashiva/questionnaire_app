from rest_framework import viewsets
from api.permissions import IsAuthorized, IsAuthorizedOrReadOnly
from base.models import PermissionByLevel, PermissionByUser
from api.serializers import PermissionByLevelSerializer, PermissionByUserSerializer

class PermissionByLevelViewSet(viewsets.ModelViewSet):
    queryset = PermissionByLevel.objects.all()
    serializer_class = PermissionByLevelSerializer
    permission_classes = (IsAuthorized,)

    def model(self):
        return 'permission'

    def get_queryset(self):
        permissionfilter = {}
        
        accesslevel = self.request.query_params.get('access_level', None)
        if accesslevel:
            permissionfilter['access_level'] = int(accesslevel)

        queryset = PermissionByLevel.objects.filter(**permissionfilter) 
        queryset = queryset.exclude(operation__id__in=IsAuthorized.GetUnsupportedPermissions())

        return queryset

class PermissionByUserViewSet(viewsets.ModelViewSet):
    queryset = PermissionByUser.objects.all()
    serializer_class = PermissionByUserSerializer
    permission_classes = (IsAuthorized,)

    def model(self):
        return 'permission'

    def get_queryset(self):
        permissionfilter = {}
        
        user = self.request.query_params.get('user', None)
        if user:
            permissionfilter['user'] = int(user)

        return PermissionByUser.objects.filter(**permissionfilter)
