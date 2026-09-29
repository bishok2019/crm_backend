# from rest_framework import filters
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from base.views import CustomGenericListView, CustomGenericRetrieveView

from .models import APILog
from .serializers import ApiLogsListSerializer, ApiLogsRetrieveSerializer


class APILogsFilter(filters.FilterSet):
    created_at = filters.DateFilter(field_name="created_at", lookup_expr="date")

    class Meta:
        model = APILog
        fields = [
            "method",
            "user_id",
            "status_code",
            "created_at",
            "created_at_bs",
        ]


class APILogsListView(CustomGenericListView):
    serializer_class = ApiLogsListSerializer
    queryset = APILog.objects.all()
    # filterset_fields = ["created_at", "created_at_bs"]
    filterset_class = APILogsFilter
    search_fields = [
        "url",
        "status_code",
        "method",
        "ip",
        # "user_id",
        # "username",
    ]

    # def get_permissions(self):
    #     return [
    #         CustomAuthenticationPermission(
    #             models={
    #                 PermissionLists.HTTP_GET_METHOD: PermissionLists.API_LOGS,
    #             },
    #         )
    #     ]
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     username = self.request.query_params.get("username")
    #     if username:
    #         User = get_user_model()
    #         try:
    #             user = User.objects.get(username__iexact=username)
    #             queryset = queryset.filter(user_id=user.id)
    #         except User.DoesNotExist:
    #             queryset = queryset.none()
    #     return queryset
    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get("username")
        print("DEBUG username param:", username)
        if username:
            User = get_user_model()
            try:
                user = User.objects.get(username__iexact=username)
                print("DEBUG user id:", user.id)
                queryset = queryset.filter(user_id=user.id)
            except User.DoesNotExist:
                print("DEBUG user not found")
                queryset = queryset.none()
        return queryset


class APILogsRetrieveView(CustomGenericRetrieveView):
    serializer_class = ApiLogsRetrieveSerializer
    queryset = APILog.objects.all()

    # def get_permissions(self):
    #     return [
    #         CustomAuthenticationPermission(
    #             models={
    #                 PermissionLists.HTTP_GET_METHOD: PermissionLists.API_LOGS,
    #             },
    #         )
    #     ]
