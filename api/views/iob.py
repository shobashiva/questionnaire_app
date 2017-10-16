import json
import sys
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from base.models import (IOB, IOBComponent, IOBComponentType)
from api.serializers import (
    IOBSerializer,
    IOBComponentSerializer,
    IOBComponentActionSerializer,
    IOBComponentTextSerializer,
    IOBComponentPeopleSerializer,
    IOBComponentResourceSerializer,
    IOBSponsorSerializer)
#from django.http import HttpResponse

#@Chris: this kind of feels like it should be part of the serializer... should it?
def IOBComponentDataRecursive(component, iob, isPublic):

    componentData = {}

    dataModel = component.iob_component_type.iob_master_component_type.data_table_id    

    if dataModel == 1: #TODO:replace this with data_model when it is available
        #text
        #might need to do error-checking here instead of calling .data immediately
        componentData = IOBComponentTextSerializer(component.iobcomponenttext).data
    elif dataModel == 2:
        #People
        componentData = IOBComponentPeopleSerializer(component.iobcomponentpeople).data
    elif dataModel == 3:
        #Resource
        componentData = IOBComponentResourceSerializer(component.iobcomponentresource).data
    elif dataModel == 4:
        #Action
        componentData = IOBComponentActionSerializer(component.iobcomponentaction).data

    fields = { 'iob_component_type__parent_component_type' : component.iob_component_type }
    if isPublic:
        fields['is_public'] = True

    #iob_component_type__parent_component_type=component.iob_component_type, is_public=isPublic
    childComponents = []
    components = component.iobcomponent_set.filter(**fields).prefetch_related('iob_component_type__iob_master_component_type', 'iobcomponentaction__iob_component_type__iob_master_component_type', 'iobcomponentaction__vote_count', 'iobcomponenttext__iob_component_type__iob_master_component_type', 'iobcomponentresource__iob_component_type__iob_master_component_type', 'iobcomponentpeople__iob_component_type__iob_master_component_type')
    for childComponent in components:
        childComponents.append(IOBComponentDataRecursive(childComponent, iob, isPublic))

    # dataModel = component.iob_component_type.iob_master_component_type.data_table_id    

    # if dataModel == 1: #TODO:replace this with data_model when it is available
    #     #text
    #     #might need to do error-checking here instead of calling .data immediately
    #     componentData = IOBComponentTextSerializer(component.iobcomponenttext).data
    # elif dataModel == 2:
    #     #People
    #     componentData = IOBComponentPeopleSerializer(component.iobcomponentpeople).data
    # elif dataModel == 3:
    #     #Resource
    #     componentData = IOBComponentResourceSerializer(component.iobcomponentresource).data
    # elif dataModel == 4:
    #     #Action
    #     componentData = IOBComponentActionSerializer(component.iobcomponentaction).data

    # childComponents = []
    # for component in component.iobcomponent_set.all():
    #     childComponents.append(IOBComponentDataRecursive(component))    
    # componentData['child_components'] = childComponents

    return componentData

def IOBComponentData(component):

    componentData = {}

    dataModel = component.iob_component_type.iob_master_component_type.data_table_id    

    if dataModel == 1: #TODO:replace this with data_model when it is available
        #text
        #might need to do error-checking here instead of calling .data immediately
        componentData = IOBComponentTextSerializer(component.iobcomponenttext).data
    elif dataModel == 2:
        #People
        componentData = IOBComponentPeopleSerializer(component.iobcomponentpeople).data
    elif dataModel == 3:
        #Resource
        componentData = IOBComponentResourceSerializer(component.iobcomponentresource).data
    elif dataModel == 4:
        #Action
        componentData = IOBComponentActionSerializer(component.iobcomponentaction).data

    return componentData

# def FindChildren(component, iob, processedChildren):

#     componentData = {}
#     if component.id in processedChildren:
#         return componentData

#     componentData['components'] = []
#     dataModel = component.iob_component_type.iob_master_component_type.data_table_id    

#     if dataModel == 1: #TODO:replace this with data_model when it is available
#         #text
#         #might need to do error-checking here instead of calling .data immediately
#         componentData = IOBComponentTextSerializer(component.iobcomponenttext).data
#     elif dataModel == 2:
#         #People
#         componentData = IOBComponentPeopleSerializer(component.iobcomponentpeople).data
#     elif dataModel == 3:
#         #Resource
#         componentData = IOBComponentResourceSerializer(component.iobcomponentresource).data
#     elif dataModel == 4:
#         #Action
#         query_list = []
#         query_list.append(component.objects.all())
#         query_list.append(component.agenda.objects.all())
#         query_list.append(component.iobcomponentaction.objects.all())
#         query_list.append(component.iob_component_type.objects.all())
        
#         componentData = IOBComponentActionSerializer(query_list).data

#     childComponents = []
#     for childComponent in iob.iobcomponent_set.filter(iob_component_type__parent_component_type=component.iob_component_type, is_public=True).select_related('iobcomponentaction'):
#         childcomponentData = FindChildren(childComponent, iob, processedChildren)
#         if len(childcomponentData) > 0:
#             childComponents.append(childcomponentData)
#         else:
#             childComponents.append(IOBComponentData(childComponent))

#     componentData['components'] = childComponents
#     processedChildren.append(component.id)
#     return componentData

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly, ))
def detailView(request, iob_id):
    response = {}

    qsIOB = IOB.objects.filter(pk=iob_id).select_related('event', 'iob_source', 'iob_type', 'topic').prefetch_related('committee')
    if qsIOB.exists():
        iob = qsIOB[0]       

        response['iob'] = {}
        response['iob']['components'] = []
        isPublic = False # TODO add is_public only when not logged in

        # processedChildren = []
        # for component in iob.iobcomponent_set.filter(is_public=True).order_by('iob_component_type'):
        #     if component.id not in processedChildren:
        #         componentData = FindChildren(component, iob, processedChildren)
        #         if componentData:
        #             response['iob']['components'].append(componentData)

        fields = { 'iob_component_type__parent_component_type': 0 }
        if isPublic:
            fields['is_public'] = True

        response['iob']['counts'] = {}
        for component_iob in iob.iobcomponent_set.all():
            if not component_iob.iob_component_type.iob_component_alias in response['iob']['counts']:
                response['iob']['counts'][component_iob.iob_component_type.iob_component_alias] = 0
            response['iob']['counts'][component_iob.iob_component_type.iob_component_alias] += 1

        components = iob.iobcomponent_set.filter(**fields).prefetch_related('agenda_set', 'iob_component_type__iob_master_component_type', 'iobcomponentaction__iob_component_type__iob_master_component_type', 'iobcomponentaction__vote_count', 'iobcomponenttext__iob_component_type__iob_master_component_type', 'iobcomponentresource__iob_component_type__iob_master_component_type', 'iobcomponentpeople__iob_component_type__iob_master_component_type')
        for component in components:
            componentData = IOBComponentDataRecursive(component, iob, isPublic)
            if componentData:
                response['iob']['components'].append(componentData)

        fields = { 'iob_component_type__parent_component_type__gt': 0 }
        if isPublic:
            fields['is_public'] = True

        components = iob.iobcomponent_set.filter(**fields).prefetch_related('iob_component_type__iob_master_component_type', 'iobcomponentaction__iob_component_type__iob_master_component_type', 'iobcomponentaction__vote_count', 'iobcomponenttext__iob_component_type__iob_master_component_type', 'iobcomponentresource__iob_component_type__iob_master_component_type', 'iobcomponentpeople__iob_component_type__iob_master_component_type')
        for component in components:
            componentData = IOBComponentData(component)
            if componentData:
                response['iob']['components'].append(componentData)

            # for component in iob.iobcomponent_set.filter(iob_component_type__parent_component_type=0, is_public=True):
            #     componentData = IOBComponentDataRecursive(component, iob, ispublic)
            #     if componentData:
            #         response['iob']['components'].append(componentData)

            # for component in iob.iobcomponent_set.filter(iob_component_type__parent_component_type__gt=0, is_public=True):
            #     componentData = IOBComponentData(component)
            #     if componentData:
            #         response['iob']['components'].append(componentData)

        # for component in iob.iobcomponent_set.filter(iob_component_type__parent_component_type__gt=0, is_public=True):
        #     componentData = IOBComponentData(component)
        #     if componentData:
        #         parent = component.iob_component_type.parent_component_type
        #         parent_alias = IOBComponentType.objects.values_list('iob_component_alias', flat=True).get(id=parent.id)
        #         alias = component.iob_component_type.iob_component_alias
        #         if not alias in response['iob']['components'][parent_alias]:
        #             response['iob']['components'][parent_alias].append(child)
        #         response['iob']['components'][parent_alias][alias].append(componentData)


        # for component_type in IOBComponentType.objects.filter(parent_component_type=0):
        #     components = []
        #     for component in iob.iobcomponent_set.filter(iob_component_type__iob_component_alias=component_type.iob_component_alias, is_public=True):
        #         componentData = IOBComponentDataRecursive(component)
        #         components.append(componentData)
        #     if len(components) > 0:
        #         response['iob']['components'][component_type.iob_component_alias] = components

        # for component_type in IOBComponentType.objects.filter(parent_component_type>0):
        #     components = []
        #     for component in iob.iobcomponent_set.filter(iob_component_type__iob_component_alias=component_type.iob_component_alias, is_public=True):
        #         componentData = IOBComponentDataRecursive(component)
        #         components.append(componentData)
        #     if len(components) > 0:
        #         parent = IOBComponentType.objects.get(parent_component_type=component_type.parent_component_type)
        #         response['iob']['components'][parent.iob_component_alias][]


        # components = []
        # for component in iob.iobcomponent_set.filter(parent_iob_component__isnull=True, is_public=True):

        #     componentData = IOBComponentDataRecursive(component)
        #     components.append(componentData)

        # response['iob']['components'] = components
        #response['temp'] = dir(iob)
        response['iob']['actionSummary'] = []
        actionSummary = {}
        for component in response['iob']['components']:
            if ('action_type' in component):
                text_title = component['action_intro']
                if not (text_title in actionSummary):
                    actionSummary[text_title] = {}
                    actionSummary[text_title]['name'] = text_title
                if (component['iob_component_type']['iob_component_alias'] == 'Committee Recommendation' or
                    component['iob_component_type']['iob_component_alias'] == 'Committee Final Action'):
                    actionSummary[text_title]['c_action'] = component['action_type']['name']
                elif (component['iob_component_type']['iob_component_alias'] == 'Assembly Action'):
                    actionSummary[text_title]['a_action'] = component['action_type']['name']

        for action in actionSummary:
            response['iob']['actionSummary'].append(actionSummary[action])
    return Response(response)

@api_view(['GET'])
def componentView(request, iob_id):
    response = {}

    qsIOB = IOB.objects.filter(pk=iob_id).select_related('event', 'iob_source', 'iob_type', 'topic').prefetch_related(
        'iobcomponent_set__iobcomponentaction__vote_count__vote_type', 
        'iobcomponent_set__iobcomponentaction__action_type', 
        'iobcomponent_set__iobcomponentaction__iob_component_type__iob_master_component_type', 
        'iobcomponent_set__iobcomponentpeople__users', 
        'iobcomponent_set__iobcomponentpeople__iob_component_type__iob_master_component_type', 
        'iobcomponent_set__iobcomponentresource__iob_component_type__iob_master_component_type', 
        'iobcomponent_set__iobcomponentresource__resource', 
        'iobcomponent_set__iobcomponenttext__iob_component_type__iob_master_component_type',
        'iobcommitteeitem_set__committee',
        'iobcomponent_set__iob_component_type',
        'iobcomponent_set__iob_component_type__iob_master_component_type')
    if qsIOB.exists():
        iob = qsIOB[0]

        response['iob'] = IOBSerializer(iob).data
        components = {}

        # Initialize the iob type dictionary
        i=0
        for iobComponentType in IOBComponentType.objects.filter(iob_type=iob.iob_type).order_by('parent_component_type'):
            components[iobComponentType.id] = {}
            components[iobComponentType.id]['display_name'] = iobComponentType.iob_component_alias
            components[iobComponentType.id]['display_order'] = i
            components[iobComponentType.id]['components'] = []
            i += 1


        # fill out the iob type dictionary with iob components
        for component_iob in iob.iobcomponent_set.all():
            if component_iob.iob_component_type.parent_component_type.id > 0:
                components[component_iob.iob_component_type.parent_component_type.id]['components'].append(IOBComponentData(component_iob))
            else:
                components[component_iob.iob_component_type.id]['components'].append(IOBComponentData(component_iob))

        response['iob']['components'] = []
        for name in components:
            response['iob']['components'].append(components[name])
    return Response(response)
