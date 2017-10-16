from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from base.models import (
    Event, 
    IOBSource,
    ActionType,
    IOBType, 
    Body, 
    IOBStatus, 
    VoteType, 
    UsStates, 
    Organization,
    AccessLevel,
    OperationGroup,
    Operation,
)
from api.serializers import (
    EventSerializer,
    IOBSourceSerializer,
    ActionTypeSerializer,
    IOBTypeSerializer,
    BodySerializer,
    IOBStatusSerializer,
    VoteTypeSerializer,
    USStatesSerializer,
    OrganizationSerializer,
    AccessLevelSerializer,
    OperationGroupSerializer,
    OperationSerializer,
)
from api.permissions import IsAuthorized

# Read-only access to populate dropdown options
class SelectOptionsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, format=None):
        supportedSources = {
            'Event': EventSerializer(Event.objects.all().order_by('-event_date'), fields=('id', 'name'), many=True).data,
            'Source': IOBSourceSerializer(IOBSource.objects.filter(client_id=1), fields=('id', 'name'), many=True).data,
            'CommitteeAction': ActionTypeSerializer(ActionType.objects.all().order_by('name'), fields=('id', 'name'), many=True).data,
            'AssemblyAction' : ActionTypeSerializer(ActionType.objects.all().order_by('name'), fields=('id', 'name'), many=True).data,
            'ActionType' : ActionTypeSerializer(ActionType.objects.all().order_by('name'), fields=('id', 'name'), many=True).data,
            'BusinessType': IOBTypeSerializer(IOBType.objects.all(), fields=('id', 'name'), many=True).data,
            'Body': BodySerializer(Body.objects.filter(client_id=1).order_by('name'), fields=('id', 'name'), many=True).data,
            'Status': IOBStatusSerializer(IOBStatus.objects.filter(is_meta_status=False), fields=('id', 'name'), many=True).data,
            'VoteType': VoteTypeSerializer(VoteType.objects.filter(), fields=('id', 'name'), many=True).data,
            'USStates': USStatesSerializer(UsStates.objects.all(), fields=('state_code', 'name'), many=True).data,
            'Organization': OrganizationSerializer(Organization.objects.filter(client_id=1), fields=('id', 'name'), many=True).data,
            'AccessLevel': AccessLevelSerializer(AccessLevel.objects.filter(client_id=1).order_by('id'), fields=('id', 'name', 'is_default'), many=True).data,
            'OperationGroup': OperationGroupSerializer(OperationGroup.objects.exclude(name='System').order_by('name'), many=True).data,
            'Operation': OperationSerializer(Operation.objects.exclude(id__in=IsAuthorized.GetUnsupportedPermissions()), many=True).data,
        }

        response = { }
        sources = request.GET.getlist('source', supportedSources)
        for source in sources:
            if source in supportedSources:
                response[source] = supportedSources[source]
            else:
                response[source] = []

        return Response(response)