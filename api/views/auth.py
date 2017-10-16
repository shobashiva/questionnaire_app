from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_expiring_authtoken.models import ExpiringToken
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
#from emailusernames.utils import create_user, get_user
from api.crypto import AESCipher
from base import models
from api.serializers import UserSerializer
from django.core import signing
#from api.permissions import IsAuthorized
from itertools import chain

@api_view(['POST'])
@permission_classes((AllowAny, ))
def login(request):
    """Respond to POSTed username/password with token and permissions."""
    serializer = AuthTokenSerializer(data=request.data)

    if serializer.is_valid():
        token, _ = ExpiringToken.objects.get_or_create(
            user=serializer.validated_data['user']
        )

        if token.expired():
            # If the token is expired, generate a new one.
            token.delete()
            token = ExpiringToken.objects.create(
                user=serializer.validated_data['user']
            )

        # get permissions
        #profile = models.UserProfile.objects.get(user=serializer.validated_data['user'])
        #level_permissions = models.PermissionByLevel.objects.filter(access_level=profile.access_level).exclude(operation__id__in=IsAuthorized.GetUnsupportedPermissions()).exclude(status_id=u'').values_list('operation', 'status_id')
        #user_permissions = models.PermissionByUser.objects.filter(user=profile).exclude(status_id=u'').values_list('operation', 'status_id')

        #result_lst = chain(user_permissions, level_permissions)

        data = {'token': token.key,}# 'permissions': result_lst, 'lookup': IsAuthorized.operation_lookup}
        return Response(data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def logout(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        if (token):
            key = token.split('Token ')
            try:
                ExpiringToken.objects.get(key=key[1]).delete()
            except:
                pass
            return Response(status=status.HTTP_200_OK)
    except:
        return Response('Failed to delete token', status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((AllowAny, ))
def forgot_password(request):
    email = request.data['email']
    user = User.objects.filter(email=email)
    if len(user) > 0:
        msg_from = settings.DEFAULT_FROM_EMAIL
        msg_to = email,
        msg_title = 'Password reset request'
        passtoken, created = ExpiringToken.objects.get_or_create(user_id=user[0].id)
        if created:
            passtoken.save()
        token = signing.dumps({'email' : email, 'passtoken': passtoken.key })
        msg_body = 'To reset your password, click on this one-time use link. You will be prompted to enter a new password.\r\n\r\n' + request.build_absolute_uri('/') + 'reset?token=' + token
        sent = send_mail(msg_title, msg_body, msg_from, msg_to, fail_silently=False)

    return Response(status=status.HTTP_200_OK) # reply success anyway

@api_view(['POST'])
@permission_classes((AllowAny, ))
def validate_reset_token(request):
    token = request.data['token']
    msg = { }
    try:
        data = signing.loads(token, max_age=900) # 15 minute expiration
    except signing.SignatureExpired:
        msg['errors'] = 'Reset password request has expired.'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    except signing.BadSignature:
        msg['errors'] = 'Invalid reset password request.'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    data_token = data['passtoken']
    email = data['email']
    if email:
        user = User.objects.get(email=email)
        passtoken = ExpiringToken.objects.filter(user_id=user.id)
        if len(passtoken) > 0 and passtoken[0].key == data_token:
            return Response(status=status.HTTP_200_OK)
        else:
            msg['errors'] = 'This password reset request cannot be used any more.' 
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    else:
        msg['errors'] = 'Missing email in password reset request.'
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny, ))
def reset_password(request):
    token = request.data['token']
    print(token)
    print(type(token))
    newpassword = request.data['newpassword']
    msg = { }
    try:
        data = signing.loads(token, max_age=900) # 15 minute expiration
    except signing.SignatureExpired:
        msg['errors'] = 'Reset password request has expired.'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    except signing.BadSignature:
        msg['errors'] = 'Invalid reset password request.'
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     msg['errors'] = 'Unexpected error'
    #     return Response(msg, status=status.HTTP_400_BAD_REQUEST)


    data_token = data['passtoken']
    email = data['email']

    if email:
        user = User.objects.get(email=email)
        passtoken = ExpiringToken.objects.filter(user_id=user.id)
        if len(passtoken) > 0 and passtoken[0].key == data_token:
            cipher = AESCipher();
            user.set_password(newpassword);
            user.save()
            passtoken.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            msg['errors'] = 'This password reset request cannot be used any more.'
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    else:
        msg['errors'] = 'Missing email in password reset request.'
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def deleteuser(request):
    email = request.data['user']
    token = request.META.get('HTTP_AUTHORIZATION')
    if (token):
        key = token.split('Token ')

    operation = IsAuthorized._get_operation(IsAuthorized, 'userDELETE')
    level_status = IsAuthorized._get_status(IsAuthorized, operation, key[1])
    if not IsAuthorized._user_has_access(IsAuthorized, None, operation, level_status):
        return Response('You do not have permission to delete this user.', status=status.HTTP_403_FORBIDDEN)

    profile = models.UserProfile.objects.get(email=email)
    if profile.access_level.id == 181:
        return Response('Cannot delete System Administrator accounts.', status=status.HTTP_403_FORBIDDEN)

    profile.delete()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    #organization = request.data['organization']
    first_name = request.data['first_name']
    last_name = request.data['last_name']
    email = request.data['email']
    password = request.data['password']

    msg = { 'errors': {} }
    if len(first_name) == 0:
        msg['errors']['first_name'] = ['This field cannot be blank.']
    if len(last_name) == 0:
        msg['errors']['last_name'] = ['This field cannot be blank.']
    if len(password) == 0:
        msg['errors']['password'] = ['This field cannot be blank.']
    
    if len(email) == 0:
        msg['errors']['email'] = ['This field cannot be blank.']
    else:
        try:
            get_user(email)
            msg['errors']['email'] = ['E-mail already exists.']
        except:
            pass

    if len(msg['errors']) > 0:
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    # if int(organization) > 0:
    #     org = models.Organization.objects.get(id=organization)
    # else:
    #     org = None

    cipher = AESCipher()
    encrypted = cipher.encrypt(password)

    try:        
        profile = models.UserProfile.objects.create(email=email, first_name=first_name, last_name=last_name, password=encrypted)#org, access_level
        user = create_user(email, password)

        user.save()
        profile.user = user
        profile.save()

        return Response(UserSerializer(user.userprofile).data)
    except IntegrityError as err:
        # unlikely event that this email hash clashes with another existing email hash
        msg['errors']['email'] = ['Unable to register with this email address.']
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as err:
        msg['errors']['email'] = [str(err)]
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])#, 'PUT'])
@permission_classes((IsAuthenticated, ))
def profile(request, token):
    # Make sure users can only change their own profile
    if not token in request.META.get('HTTP_AUTHORIZATION'):
        msg = { 'errors': 'Invalid token' }
        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)

    user_id = request.query_params.get('user_id', None)

    # if user_id is not None:
    #     operation = IsAuthorized._get_operation(IsAuthorized, 'userPUT')
    #     level_status = IsAuthorized._get_status(IsAuthorized, operation, token)
    #     if not IsAuthorized._user_has_access(IsAuthorized, None, operation, level_status):
    #         return Response('You do not have permission to edit this user\'s profile.', status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if user_id is not None:
            profile = models.UserProfile.objects.get(id=user_id)
            return Response(UserSerializer(profile).data)
        else: 
            token = ExpiringToken.objects.get(key=token)
            profile = models.UserProfile.objects.get(user=token.user)
            return Response(UserSerializer(profile).data)
    # elif request.method == 'PUT':
    #     # validate the incoming data
    #     if request.data['organization'] == 0:
    #         request.data['organization'] = None
    #     serializer = UserSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     first_name = request.data['first_name']
    #     last_name = request.data['last_name']
    #     msg = { 'errors': {} }
    #     if len(first_name) == 0:
    #         msg['errors']['first_name'] = ['This field cannot be blank.']
    #     if len(last_name) == 0:
    #         msg['errors']['last_name'] = ['This field cannot be blank.']
    #     if len(msg['errors']) > 0:
    #         return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    #     if user_id is not None:
    #         profile = models.UserProfile.objects.get(id=user_id)
    #     else: 
    #         token = ExpiringToken.objects.get(key=token)
    #         profile = models.UserProfile.objects.get(user=token.user)

    #     org = request.data.get('organization', None)
    #     if (org is not None):
    #         organization = models.Organization.objects.get(id=org)
    #         profile.organization = organization
    #     profile.first_name = request.data.get('first_name', profile.first_name)
    #     profile.last_name = request.data.get('last_name', profile.last_name)
    #     profile.phone1 = request.data.get('phone1', profile.phone1)
    #     profile.phone2 = request.data.get('phone2', profile.phone2)
    #     profile.other_info = request.data.get('other_info', profile.other_info)

    #     profile.save()

    #     return Response(UserSerializer(profile).data)
    else:
        msg = { 'errors': 'Unsupported Method: ' + request.method }
        return Response(msg, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def change_password(request, token):
    # Make sure users can only change their own password
    if not token in request.META.get('HTTP_AUTHORIZATION'):
        msg = { 'errors': 'Invalid token' }
        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        # validate the incoming data
        currentpassword = request.data['currentpassword']
        newpassword = request.data['newpassword']
        msg = { 'errors': {} }
        if len(currentpassword) == 0:
            msg['errors']['currentpassword'] = ['This field cannot be blank.']
        if len(newpassword) == 0:
            msg['errors']['newpassword'] = ['This field cannot be blank.']
        if len(msg['errors']) > 0:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        token = ExpiringToken.objects.get(key=token)
        profile = models.UserProfile.objects.get(user=token.user)

        cipher = AESCipher()
        encrypted = cipher.encrypt(currentpassword)
        if (profile.password != encrypted.decode('utf-8')):
            msg['errors']['currentpassword'] = ['Invalid password.']
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        cipher = AESCipher()
        profile.password = cipher.encrypt(newpassword)

        profile.save()

        return Response(UserSerializer(profile).data)
    else:
        msg = { 'errors': 'Unsupported Method: ' + request.method }
        return Response(msg, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# @api_view(['POST'])
# @permission_classes((IsAuthenticated, ))
# def unlock(request):
#     token = request.META.get('HTTP_AUTHORIZATION')
#     if (token):
#         key = token.split('Token ')

#     operation = IsAuthorized._get_operation(IsAuthorized, 'userPOST')
#     level_status = IsAuthorized._get_status(IsAuthorized, operation, key[1])
#     if not IsAuthorized._user_has_access(IsAuthorized, None, operation, level_status):
#         return Response('You do not have permission to unlock this user\'s password.', status=status.HTTP_403_FORBIDDEN)

#     userid = request.data['user']
#     password = request.data['password']

#     profile = models.UserProfile.objects.get(id=userid)
#     if profile.access_level.id == 181:
#         return Response('Cannot change System Administrator password.', status=status.HTTP_403_FORBIDDEN)

#     cipher = AESCipher()
#     profile.password = cipher.encrypt(password)
#     profile.save()

#     return Response(UserSerializer(profile).data)