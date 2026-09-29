from rest_framework import serializers

from base.serializers import BaseModelSerializer, ExcludeFields

from .models import APILog


class APILogExcludeFields:
    exclude = ExcludeFields.exclude + [
        "body",
        "response",
        "header",
    ]


class ApiLogsListSerializer(BaseModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        if obj.user_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(id=obj.user_id)
                return user.username
            except User.DoesNotExist:
                return None
        return None

    class Meta:
        model = APILog
        # exclude = APILogExcludeFields.exclude
        fields = [
            "id",
            "url",
            "os_type",
            "device_type",
            "method",
            "ip",
            "user_agent",
            "system_details",
            "user_id",
            "extra_field",
            "status_code",
            "created_at",
            "created_by",
            "username",
        ]


class ApiLogsRetrieveSerializer(BaseModelSerializer):
    class Meta:
        model = APILog
        exclude = [
            "deleted_at",
        ]
