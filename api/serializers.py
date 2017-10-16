from django.db.models import Max
from rest_framework import serializers
import json
from base.models import (
    UserProfile,
)

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    
    See: http://tomchristie.github.io/rest-framework-2-docs/api-guide/serializers
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class UserSerializer(DynamicFieldsModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    first_last_name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return str(obj.last_name + ', ' + obj.first_name)

    def get_first_last_name(self, obj):
        return str(obj.first_name + ' ' + obj.last_name)

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'first_last_name', 'first_name', 'last_name', 'email', 'phone1', 'phone2', 'other_info')
