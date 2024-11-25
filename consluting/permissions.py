from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework.permissions import BasePermission

from .models import Expert,ChatRoom

class IsExpert(BasePermission):
    def has_permission(self, request, view):
        return bool(type(request.user) is not AnonymousUser and request.user.is_expert)

class IsExpertAndRegistered(BasePermission):
    def has_permission(self, request, view):
        if bool(type(request.user) is not AnonymousUser and request.user.is_expert):
            try:
                Expert.objects.get(user=request.user)
                return True
            except Expert.DoesNotExist:
                return False
        return False
    

#class OneOfTheParticipiants(BasePermission):
#    def has_permission(self, request, view):
#        res = ChatRoom.objects.select_related('user').select_related('expert').filter(id=view.kwargs.get("chat_pk"))
#        if res.exists:
#            if res.first().user_id == request.user.id or res.first().expert_id ==request.user.id:
#                return True
#        return False