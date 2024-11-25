from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('expert',views.ExpertViewSet)
router.register('favorites',views.FavoriteExpertViewSet,basename='favorites')
router.register('votes',views.VoteViewSet,basename='votes')
router.register('chats',views.ChatsViewSet,basename='chats')
router.register('consultings',views.ConsultingViewSet,basename='consultings')
router.register('expert-profile/conslutings',views.ExpertConslutingViewSet, basename='profile-conslutings')
router.register('expert-profile/free-times',views.FreeDayViewSet, basename='profile-free-times')
router.register('expert-profile/work-times',views.WorkDayViewSet, basename='profile-work-times')

chat_messages_router = routers.NestedDefaultRouter(router,'chats',lookup='chat')
chat_messages_router.register('chat-messages',views.ChatMessageViewSet,basename='chat-message')
expert_free_time_router = routers.NestedDefaultRouter(router,'expert',lookup='expert')
expert_free_time_router.register('free-times',views.ExpertFreeDayViewSet,basename='expert-free-time')

urlpatterns = [
    path('expert-profile/',views.ExpertProfileViewSet.as_view()),
] + router.urls + chat_messages_router.urls + expert_free_time_router.urls