import django_filters
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from api.permissions import IsAuthorized, IsAuthorizedOrReadOnly
from api.utils import IOBComponentHelper
from base.models import (
    Committee, 
    IOBSponsor, 
    Organization, 
    Client,
    Event, 
    Body, 
    Agency, 
    UserProfile, 
    IOB, 
    IOBComponent, 
    IOBComponentAction, 
    IOBComponentText, 
    IOBComponentPeople, 
    IOBComponentResource,
    IOBCommitteeItem,
    Resource,
    AccessLevel,
)
from api.serializers import (
    IOBViewSerializer,
    IOBComponentSerializer,
    IOBComponentActionSerializer,
    IOBComponentTextSerializer,
    IOBComponentPeopleSerializer,
    IOBComponentResourceSerializer,
    ComponentTextSerializer,
    ComponentPeopleSerializer,
    ComponentResourceSerializer,
    ComponentActionSerializer,
    IOBSerializer,
    CommitteeSerializer,
    OrganizationSerializer,
    BodySerializer,
    AgencySerializer,
    UserSerializer,
    UserPermissionsSerializer,
    AccessLevelSerializer,
    ComponentPeopleUserSerializer,
    ResourceSerializer,
)

###### Read-only viewsets ###########

class IOBSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IOB.objects.all()
    serializer_class = IOBViewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):

        iobfilter = { 
            'client_id': 1,
            'is_deleted': False,
        }

        iobId = self.request.query_params.get('iob_id', None)
        if (iobId):
            iobfilter['iob'] = iobId

        eventId = self.request.query_params.get('event_id', None)
        if (eventId):
            iobfilter['event'] = eventId

        sourceId = self.request.query_params.get('source', None)
        if sourceId is not None:
            iobfilter['iob_source'] = sourceId 

        businessTypeId = self.request.query_params.get('businessType', None)
        if (businessTypeId):
            iobfilter['iob_type'] = businessTypeId

        statusId = self.request.query_params.get('status', None)
        if (statusId):
            iobfilter['status'] = statusId

        publicId = self.request.query_params.get('publicview', None)
        if (publicId):
            if publicId == '1':
                iobfilter['is_public'] = True
            elif publicId == '2':
                iobfilter['is_public'] = False

        # showitemsId = self.request.query_params.get('showitems', None)

        if (iobId is not None and int(iobId) > 0):
            queryset = IOB.objects.filter(**iobfilter)
        else:
            queryset = IOB.objects.filter(**iobfilter).select_related('event', 'iob_source', 'iob_type').prefetch_related(Prefetch('iobcommitteeitem_set', to_attr='prefetch_iobcommitteeitem'), Prefetch('iobcomponent_set', to_attr='prefetch_iobcomponent'))

            committeeId = self.request.query_params.get('committee', None)
            if committeeId is not None:
                iobs = IOBCommitteeItem.objects.filter(iob__in=queryset, committee_id=committeeId).values('iob')
                queryset = queryset.filter(id__in=iobs)

            bodyId = self.request.query_params.get('bodyName', None)
            if bodyId is not None:
                bodyIOBs = IOBCommitteeItem.objects.filter(iob__in=queryset, committee__body__id=bodyId).values('iob')
                queryset = queryset.filter(id__in=bodyIOBs)

            c_actionId = self.request.query_params.get('c_action', None)
            if c_actionId is not None:
                c_actionfilter = {}
                c_actionfilter['iob_component_type__iob_component_alias__in'] = ['Committee Final Action', 'Committee Recommendation']

                if int(c_actionId) <= 0:
                    c_actionfilter['iobcomponentaction__action_type__id__gt'] = 0
                else:
                    c_actionfilter['iobcomponentaction__action_type__id'] = int(c_actionId)

                if int(c_actionId) == 0:
                    excludeIOBs = IOBComponent.objects.filter(iob__id__in=queryset,**c_actionfilter).values('iob')
                    cactionIOBs = IOBComponent.objects.filter(iob__id__in=queryset).exclude(iob__id__in=excludeIOBs).values('iob')
                else:
                    cactionIOBs = IOBComponent.objects.filter(iob__id__in=queryset, **c_actionfilter).values('iob')
                queryset = queryset.filter(id__in=cactionIOBs)

            a_actionId = self.request.query_params.get('a_action', None)
            if a_actionId is not None:
                a_actionfilter = {}
                a_actionfilter['iob_component_type__iob_component_alias'] = 'Assembly Action'

                if int(a_actionId) <= 0:
                    a_actionfilter['iobcomponentaction__action_type__id__gt'] = 0
                else:
                    a_actionfilter['iobcomponentaction__action_type__id'] = int(a_actionId)

                if int(a_actionId) == 0:
                    excludeIOBs = IOBComponent.objects.filter(iob__id__in=queryset,**a_actionfilter).values('iob')
                    aactionIOBs = IOBComponent.objects.filter(iob__id__in=queryset).exclude(iob__id__in=excludeIOBs).values('iob')
                else:
                    aactionIOBs = IOBComponent.objects.filter(iob__id__in=queryset, **a_actionfilter).values('iob')

                queryset = queryset.filter(id__in=aactionIOBs)

            voteType = self.request.query_params.get('voteType', None)
            if voteType is not None:
                voteTypeIOBs = IOBComponentAction.objects.filter(iob__id__in=queryset, iob_component_type__iob_component_alias__in=['Committee Final Action', 'Committee Recommendation'], vote_count__vote_type__id=int(voteType)).values('iob')
                queryset = queryset.filter(id__in=voteTypeIOBs)

            sponsorId = self.request.query_params.get('sponsor', None)
            if sponsorId is not None:
                queryset = queryset.filter(sponsors__iob_sponsor_id=int(sponsorId))

        return queryset

class SponsorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View sponsors.
    """
    queryset = IOBSponsor.objects.all()
    serializer_class = IOBSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    response = { }

    def get_serializer_class(self):
        iob_source = self.request.query_params.get('iob_source', None)
        if iob_source == 'Presbytery':
            return OrganizationSerializer
        elif iob_source == 'Agencies':
            return AgencySerializer
        elif iob_source == 'Comissioners':
            return UserSerializer
        elif iob_source == 'Committee':
            return CommitteeSerializer
        elif iob_source == 'Body':
            return BodySerializer
        else:
            return BodySerializer

    def get_queryset(self):
        iob_source = self.request.query_params.get('iob_source', None)

        queryset = { }
        if iob_source == 'Presbytery':
            queryset = Organization.objects.filter(client__pk=1).order_by('name')
        elif iob_source == 'Agencies':
            queryset = Agency.objects.filter(client__pk=1).order_by('name')
        elif iob_source == 'Comissioners':
            queryset = UserProfile.objects.filter(access_level__name='Commissioner').order_by('last_name', 'first_name')
        elif iob_source == 'Committee':
            event_id = self.request.query_params.get('event_id', None)
            if (event_id):
                queryset = Committee.objects.filter(event__pk__in=(event_id, 297)).order_by('event_id', 'name')
            else:
                queryset = Committee.objects.all().order_by('committee_no')
        elif iob_source == 'Body':
            queryset = Body.objects.filter(client__pk=1).order_by('name')
        else:
            queryset = Body.objects.none()

        return queryset

###### Restricted access viewsets ############

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'email')
    serializer_class = UserPermissionsSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'permission'

    def get_queryset(self):
        return UserProfile.objects.filter(client_id=1)

# IOB components
class RationaleViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentText.objects.all()
    serializer_class = ComponentTextSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'rationale'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Rationale')

        return IOBComponentText.objects.filter(**params)

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentText.objects.all()
    serializer_class = ComponentTextSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'recommendation'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Recommendation')

        return IOBComponentText.objects.filter(**params)

class CommentsViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentText.objects.all()
    serializer_class = ComponentTextSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'comments'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Comments')

        return IOBComponentText.objects.filter(**params)

class ConcurrencesViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentText.objects.all()
    serializer_class = ComponentTextSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'concurrences'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Concurrences')

        return IOBComponentText.objects.filter(**params)

class FinancialImplicationsViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentText.objects.all()
    serializer_class = ComponentTextSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'financialimplications'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Financial Implications')

        return IOBComponentText.objects.filter(**params)

# used for populating advocates and resource people
class ComponentPeopleViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'email')
    serializer_class = ComponentPeopleUserSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'resourcepeople'

    def get_queryset(self):
        return UserProfile.objects.filter(client_id=1)

class AdvocatesViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentPeople.objects.all()
    serializer_class = ComponentPeopleSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'advocates'

    def get_queryset(self):
        return IOBComponentPeople.objects.filter(iob_component_type__iob_master_component_type__name='Advocates')

class ResourcePeopleViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentPeople.objects.all()
    serializer_class = ComponentPeopleSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'resourcepeople'

    def get_queryset(self):
        return IOBComponentPeople.objects.filter(iob_component_type__iob_master_component_type__name='ResourcePeople')

class InformationViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentResource.objects.all()
    serializer_class = ComponentResourceSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'information'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Information')

        return IOBComponentResource.objects.filter(**params)

class MinorityReportViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentAction.objects.all()
    serializer_class = ComponentActionSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'minorityreport'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Minority Report')

        return IOBComponentAction.objects.filter(**params)

class CommitteeRecommendationViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentAction.objects.all()
    serializer_class = ComponentActionSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'committeerecommendation'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Committee Recommendation')

        return IOBComponentAction.objects.filter(**params)

class AssemblyActionViewSet(viewsets.ModelViewSet):
    queryset = IOBComponentAction.objects.all()
    serializer_class = ComponentActionSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'assemblyaction'

    def get_queryset(self):
        params = IOBComponentHelper.build_filter(self, 'Assembly Action')

        return IOBComponentAction.objects.filter(**params)

# IOB Component

class IOBComponentViewSet(viewsets.ModelViewSet):
    queryset = IOBComponent.objects.all()
    serializer_class = IOBComponentSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def model(self):
        return 'iobcomponent'

    def retrieve(self, request, pk=None):
        queryset = IOBComponent.objects.all()
        component = get_object_or_404(queryset, pk=pk)
        return Response(IOBComponentSerializer(component).data)

    def get_queryset(self):
        iobId = self.request.query_params.get('iob_id', None)
        return IOBComponent.objects.filter(iob=iobId)

class IOBViewSet(viewsets.ModelViewSet):
    queryset = IOB.objects.all()
    serializer_class = IOBSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def get_queryset(self):
        iobfilter = {}
        
        eventId = self.request.query_params.get('event_id', None)
        if (eventId):
            iobfilter['event'] = eventId

        queryset = IOB.objects.filter(**iobfilter)

        return queryset

class CommitteeFilter(django_filters.FilterSet):
    event_id = django_filters.ModelChoiceFilter(queryset=Event.objects.all())
    
    class Meta:
        model = Committee
        fields = ['event_id', 'body']

class CommitteeViewSet(viewsets.ModelViewSet):
    """
    View and edit committees
    """
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CommitteeFilter
    permission_classes = (IsAuthorizedOrReadOnly, )

    def model(self):
        return 'committee'

    def get_queryset(self):
        queryset = Committee.objects.filter(client_id=1).order_by('committee_no')
        return queryset

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    View and edit organizations
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthorized, )

    def model(self):
        return 'organization'

    def get_queryset(self):
        return Organization.objects.filter(client_id=1)

class AccessLevelViewSet(viewsets.ModelViewSet):
    """
    View and edit access levels
    """
    queryset = AccessLevel.objects.all()
    serializer_class = AccessLevelSerializer
    permission_classes = (IsAuthorized, )

    def model(self):
        return 'accesslevel'

    def get_queryset(self):
        return AccessLevel.objects.filter(client_id=1).order_by('id')

class UserLevelViewSet(viewsets.ModelViewSet):
    """
    View and edit user levels
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserPermissionsSerializer
    permission_classes = (IsAuthorized, )

    def model(self):
        return 'accesslevel'

    def get_queryset(self):
        return UserProfile.objects.filter(client_id=1)

class ResourcesViewSet(viewsets.ModelViewSet):
    """
    View and edit resources
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthorizedOrReadOnly, )

    def model(self):
        return 'resource'

    def get_queryset(self):
        event_id = self.request.query_params.get('event_id', None)
        if (event_id):
            queryset = Resource.objects.filter(client_id=1, event__pk=event_id, iob_id=None).order_by('title')
        else:
            queryset = Resource.objects.filter(client_id=1)

        return queryset

