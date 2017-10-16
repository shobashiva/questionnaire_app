#from django.contrib.auth.models import User
#from emailusernames.utils import get_user
from django.contrib.auth import get_user_model
User = get_user_model()
from api.crypto import AESCipher

class AESBackend(object):

    # def get_user(self, username):
    #     try:
    #         user = User.objects.get(email=username)
    #         return get_user(user.email)
    #     except User.DoesNotExist:
    #         return None

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)

            cipher = AESCipher()
            encrypted = cipher.encrypt(password).decode('utf-8')
            if encrypted == user.password:
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    