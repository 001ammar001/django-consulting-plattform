from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import APIView,action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from consluting.pagination import DefaultPagination
from .custom_view_sets import ListOnlyViewSet,ListCreateDestroyViewSet,ListCreateViewSet
from .permissions import IsExpert,IsExpertAndRegistered
from .models import Expert,ExpertConsluting,FavoriteExpert,Vote,ChatRoom,ChatMessage,Consluting,FreeDay,WorkDay
from . import serializers

from datetime import datetime

class ExpertViewSet(ModelViewSet):
    queryset = Expert.objects.select_related('user').prefetch_related('conslutings__consulting').all()
    filter_backends = [SearchFilter]
    search_fields = ['user__username']
    http_method_names = ["post","get"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AddExpertSerializer
        elif self.action == 'retrieve':
            return serializers.RetriveExpertSerializer
        return serializers.ListExpertSerializer

    def get_serializer_context(self):
        return {'user':self.request.user}
    
    #def get_permissions(self):
    #    if self.request.method == "POST":
    #        return [IsExpert()]
    #    return [IsAuthenticated()]
    
class ExpertConslutingViewSet(ListCreateDestroyViewSet):
    serializer_class = serializers.ExpertConslutingSerializer
    permission_classes = [IsExpertAndRegistered]

    def get_queryset(self):
        return ExpertConsluting.objects.prefetch_related('consulting').filter(expert_id=self.request.user.id)
    
    def get_serializer_context(self):
        return {'user':self.request.user}
    
class ExpertProfileViewSet(APIView):
    http_method_names = ['patch','get']
    permission_classes = [IsExpertAndRegistered]

    def get(self,request):
        expert = Expert.objects.select_related('user').prefetch_related('conslutings__consulting').get(user=request.user.id)
        serializer = serializers.RetriveExpertSerializer(expert)
        return Response(serializer.data)
    
    def patch(self,request):
        expert = Expert.objects.select_related('user').prefetch_related('conslutings__consulting').get(user=request.user.id)
        serializer = serializers.UpdateExpertSerializer(expert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class FavoriteExpertViewSet(ListOnlyViewSet):
    
    serializer_class = serializers.FavoritesExpertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteExpert.objects.prefetch_related("expert__user").filter(user=self.request.user).all()
    
    @action(detail=False,methods=['post','delete'],url_path='(?P<expert_id>\d+)')
    def add_or_delete_favorite_expert(self,request,expert_id):
        context = {'user_id':request.user.id,'expert_id':int(expert_id)}
        if request.method == "POST":
            serializer = serializers.FavoritesExpertSerializer(data=request.data,context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == "DELETE":
            fav = get_object_or_404(FavoriteExpert,**context)
            fav.delete()
            return Response({"message":"deleteed sucssesful"})

class VoteViewSet(ListOnlyViewSet):
    
    serializer_class = serializers.VoteForExpertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.prefetch_related("expert__user").filter(user=self.request.user).all()
    
    @action(detail=False,methods=['post','delete'],url_path='(?P<expert_id>\d+)')
    def add_or_delete_vote(self,request,expert_id):
        context = {'user_id':request.user.id,'expert_id':int(expert_id)}
        if request.method == "POST":
            serializer = serializers.VoteForExpertSerializer(data=request.data,context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == "DELETE":
            fav = get_object_or_404(Vote,**context)
            fav.delete()
            return Response({"message":"deleteed sucssesful"})

class ChatsViewSet(ListOnlyViewSet):
    serializer_class = serializers.ChatsListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.prefetch_related("expert__user").prefetch_related('user').filter(Q(user_id=self.request.user.id) | Q(expert_id=self.request.user.id)).all()
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}

    @action(detail=False,methods=['post'],url_path='(?P<expert_id>\d+)')
    def create_chat_room(self,request,expert_id):
        context = {'user_id':request.user.id,'expert_id':int(expert_id)}
        if request.method == "POST":
            serializer = serializers.ChatsListSerializer(data=request.data,context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class ChatMessageViewSet(ListCreateViewSet):
    serializer_class = serializers.ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        res = ChatRoom.objects.select_related('user').select_related('expert').filter(id=kwargs["chat_pk"])
        if res.exists:
            if res.first().user_id == request.user.id or res.first().expert_id ==request.user.id:
                return super().list(request, *args, **kwargs)
        return Response({'error':'you dont have permissions'},401)

    def get_serializer_context(self):
        return {'user_id':self.request.user.id,'chat_pk':self.kwargs['chat_pk']}
    
    def get_queryset(self):
        return ChatMessage.objects.select_related('chat_room').filter(chat_room_id=self.kwargs['chat_pk']).order_by('-id')
    
class ConsultingViewSet(ListOnlyViewSet):
    queryset = Consluting.objects.all()
    serializer_class = serializers.ConslutingsSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title']

class FreeDayViewSet(ModelViewSet):
    serializer_class = serializers.FreeDaySerializer
    permission_classes = [IsExpertAndRegistered]

    def get_serializer_context(self):
        return {'expert_id':self.request.user.id}

    def get_queryset(self):
        return FreeDay.objects.prefetch_related('free_times').filter(expert_id=self.request.user.id,date__gte=datetime.now())
    
class WorkDayViewSet(ListOnlyViewSet):
    serializer_class = serializers.WorkDaySerializer
    permission_classes = [IsExpertAndRegistered]

    def get_queryset(self):
        return WorkDay.objects.prefetch_related('work_times').filter(expert_id=self.request.user.id,date__gte=datetime.now())
    
class ExpertFreeDayViewSet(ListCreateViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateWorkTimeSerializer
        return serializers.FreeDaySerializer

    def get_serializer_context(self):
        return {"expert_id":int(self.kwargs['expert_pk']),"my_id":self.request.user.id}

    def get_queryset(self):
        return FreeDay.objects.prefetch_related('free_times').filter(expert_id=self.kwargs['expert_pk'],date__gte=datetime.now())