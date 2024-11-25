from django.db import transaction
from rest_framework import serializers
from .models import Expert,Consluting,ExpertConsluting,FavoriteExpert,Vote,ChatRoom,ChatMessage,FreeTime,FreeDay,WorkDay,WorkTime,Wallet

class ConslutingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consluting
        fields = ['id','title']

class ExpertConslutingSerializer(serializers.ModelSerializer):
    consulting = serializers.StringRelatedField(read_only=True)
    expert_conslutings = serializers.ListField(child=serializers.CharField(max_length=255),write_only=True)
    class Meta:
        model = ExpertConsluting
        fields = ['id','consulting','expert_conslutings']

    def validate_expert_conslutings(self,value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError({'error':'dublicates are not alowed in conslutings'})
        return value
    
    def save(self, **kwargs):
        expert = Expert.objects.get(user=self.context["user"])
        (new_cons,old_cons) = prepare_consluting(self.validated_data,expert,True)
        with transaction.atomic():
            created_conslutings = [Consluting.objects.create(title=item) for item in new_cons]
            all_cons = created_conslutings + old_cons
            conslutings = [ExpertConsluting(expert=expert,consulting=item) for item in all_cons]
            cons = ExpertConsluting.objects.bulk_create(conslutings)
            return cons
        
class ListExpertSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.SerializerMethodField(method_name='get_user_name')
    class Meta:
        model = Expert
        fields = ['user','price','image','user_name']

    def get_user_name(self,expert):
        return expert.user.username

class RetriveExpertSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    conslutings = ExpertConslutingSerializer(many=True)
    class Meta:
        model = Expert
        fields = ['user','country','city','street','phone_number','price','image','conslutings']

class AddExpertSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    expert_conslutings = serializers.ListField(child=serializers.CharField(max_length=255),write_only=True)
    class Meta:
        model = Expert
        fields = ['user','country','city','street','phone_number','price','image','expert_conslutings']

    def validate(self, attrs):
        try:
            Expert.objects.get(user=self.context['user'])
            raise serializers.ValidationError({'error':'this user has already registared as an expert'})
        except Expert.DoesNotExist:
            return super().validate(attrs)

    def validate_expert_conslutings(self,value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError({'expert_conslutings':"dublicates are not allowed"})
        return value

    def create(self, validated_data):
        (con_list,query_set_list) = prepare_consluting(validated_data,"",False)
        with transaction.atomic():
            expert = Expert.objects.create(user=self.context['user'],**validated_data)
            created_conslutings = [Consluting.objects.create(title=item) for item in con_list]
            all_cons = created_conslutings + query_set_list
            conslutings = [ExpertConsluting(expert=expert,consulting=item) for item in all_cons]
            ExpertConsluting.objects.bulk_create(conslutings)
            return expert      

class UpdateExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = ['country','city','street','phone_number','price','image']

class FavoritesExpertSerializer(serializers.ModelSerializer):
    expert = ListExpertSerializer(read_only=True)
    class Meta:
        model = FavoriteExpert
        fields = ['id','expert']

    def validate(self, attrs):
        if self.context['expert_id'] == self.context['user_id']:
            raise serializers.ValidationError({'error':'you cant add yourself to favorite'})
        try:
            Expert.objects.get(user_id=self.context['expert_id'])
        except Expert.DoesNotExist:
            raise serializers.ValidationError({"erorr":"no expert found with this id"})
        try:
            FavoriteExpert.objects.get(user_id=self.context['user_id'],expert_id=self.context['expert_id'])
            raise serializers.ValidationError({'error':'you already added this expert to favoirte'})
        except FavoriteExpert.DoesNotExist:
            return super().validate(attrs)
        
    def create(self, validated_data):
        instance = FavoriteExpert.objects.create(user_id=self.context['user_id'],expert_id=self.context['expert_id'])
        return instance        

class VoteForExpertSerializer(serializers.ModelSerializer):
    expert = ListExpertSerializer(read_only=True)
    class Meta:
        model = Vote
        fields = ['expert','rate']

    def validate(self, attrs):
        if self.context['expert_id'] == self.context['user_id']:
            raise serializers.ValidationError({'error':'you cant vote for yourself'})
        try:
            Expert.objects.get(user_id=self.context['expert_id'])
        except Expert.DoesNotExist:
            raise serializers.ValidationError({"erorr":"no expert found with this id"})
        return super().validate(attrs)
    
    def save(self, **kwargs):
        try:
            vote = Vote.objects.get(user_id=self.context['user_id'],expert_id=self.context['expert_id'])
            vote.rate = self.validated_data['rate']
            vote.save()
            self.instance = vote
        except Vote.DoesNotExist:
            self.instance = Vote.objects.create(user_id=self.context['user_id'],expert_id=self.context['expert_id'],**self.validated_data)
        return self.instance

class ChatsListSerializer(serializers.ModelSerializer):
    other_member = serializers.SerializerMethodField(method_name='get_other_member',read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id','other_member']
    
    def get_other_member(self,room):
        user_id = self.context['user_id']
        if user_id == room.user.id:
            return room.expert.user.id
        return room.user.id

    def validate(self, attrs):
        user_id = self.context['user_id']
        expert_id = self.context['expert_id']
        if user_id == expert_id:
            raise serializers.ValidationError({'error':'you cant create a chat with your self'})
        try:
            Expert.objects.get(user_id=expert_id)
        except Expert.DoesNotExist:
            raise serializers.ValidationError({"error":"No expert found with this id"})
        try:
            ChatRoom.objects.get(user_id=user_id,expert_id=expert_id)
            raise serializers.ValidationError({'error':'CharRoom already exist'})
        except ChatRoom.DoesNotExist:
            return super().validate(attrs)
        
    def save(self, **kwargs):
        self.instance = ChatRoom.objects.create(user_id=self.context['user_id'],expert_id=self.context['expert_id'])
        return self.instance

class ChatMessageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ChatMessage
        fields = ['user','message']

    def save(self, **kwargs):
        print(self.context)
        self.instance = ChatMessage.objects.\
                                    create(user_id=self.context['user_id'],
                                           chat_room_id=self.context['chat_pk'],
                                           **self.validated_data)
        return self.instance

class FreeTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeTime
        fields = ['free_day','start_time']

class CreateWorkTimeSerializer(serializers.ModelSerializer):
    date_id = serializers.IntegerField(write_only=True)
    time = serializers.TimeField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    work_day = serializers.PrimaryKeyRelatedField(read_only=True)
    start_time = serializers.TimeField(read_only=True)
    class Meta:
        model = WorkTime
        fields = ['date_id','time','user','work_day','start_time']

    def validate(self, attrs):
        print(self.context)
        if self.context['expert_id'] == self.context['my_id']:
            raise serializers.ValidationError({"error":"you cant book appointment with your self"})
        return super().validate(attrs)


    def save(self, **kwargs):
        time = self.validated_data.get('time')
        day_id = self.validated_data.get('date_id')
        my_id = self.context['my_id']
        expert_id = self.context['expert_id']
        try:
            free_time = FreeTime.objects.select_related('free_day').get(free_day_id=day_id,start_time=time)
            with transaction.atomic():
                my_wallet = Wallet.objects.get(user_id=my_id)
                expert = Expert.objects.select_related('user__wallet').get(user_id=expert_id)
                my_wallet.account = my_wallet.account - expert.price
                expert.user.wallet.account = expert.user.wallet.account + expert.price
                expert.save()
                my_wallet.save()
                try:
                    work_day = WorkDay.objects.get(expert_id=self.context['expert_id'],date=free_time.free_day.date)
                    work_time = WorkTime.objects.create(work_day=work_day,start_time=time,user_id=my_id)
                except WorkDay.DoesNotExist:
                    work_day = WorkDay.objects.create(expert_id=self.context['expert_id'],date=free_time.free_day.date)
                    work_time = WorkTime.objects.create(work_day=work_day,start_time=time,user_id=my_id)
                free_time.delete()
                self.instance = work_time

                return self.instance

        except FreeTime.DoesNotExist:
            raise serializers.ValidationError({"error":"no such time exist for this expert"})


class FreeDaySerializer(serializers.ModelSerializer):
    free_times = FreeTimeSerializer(many=True,read_only=True)
    start_times = serializers.ListSerializer(child=serializers.TimeField(),write_only=True)
    end_times = serializers.ListSerializer(child=serializers.TimeField(),write_only=True)
    
    class Meta:
        model = FreeDay
        fields = ['id','date','free_times','start_times','end_times']
        
    def save(self, **kwargs):
        start_times = self.validated_data.pop('start_times')
        end_times = self.validated_data.pop('end_times')
        validate_times(start_times,end_times)
        app_start_times = []
        for i in range(len(start_times)):        
            while(start_times[i] != end_times[i]):
                app_start_times.append(start_times[i])
                old_minute = start_times[i].minute
                start_times[i] = start_times[i].replace(minute=(start_times[i].minute+30)%60)
                if old_minute >= start_times[i].minute:
                    start_times[i] = start_times[i].replace(hour=(start_times[i].hour+1)%24)
        with transaction.atomic():
            try:
                self.instance = FreeDay.objects.get(expert_id=self.context['expert_id'],date = self.validated_data.get('date'))
                existed_times = list(FreeTime.objects.filter(free_day=self.instance).values_list("start_time",flat=True))
                for item in existed_times:
                    if item in app_start_times:
                        app_start_times.remove(item)
                print(app_start_times)
                free_times = [FreeTime(free_day=self.instance,start_time= item) for item in app_start_times]
                FreeTime.objects.bulk_create(free_times)
            except FreeDay.DoesNotExist:
                self.instance = FreeDay.objects.create(expert_id=self.context['expert_id'],**self.validated_data)
                free_times = [FreeTime(free_day=self.instance,start_time= item) for item in app_start_times]
                FreeTime.objects.bulk_create(free_times)
            return self.instance

class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = ['work_day','start_time','user']

class WorkDaySerializer(serializers.ModelSerializer):
    work_times = WorkTimeSerializer(many=True)
    class Meta:
        model = WorkDay
        fields = ['date','work_times']

def validate_times(start_times,end_times):
    len_start = len(start_times)
    len_end = len(end_times)
    if len_start != len_end:
        raise serializers.ValidationError({'error':'start times and end times must have the same length'})
    for i in range(len_start):
        if start_times[i] > end_times[i] or start_times[i] == end_times[i]:
            raise serializers.ValidationError({'error':f'end time {i} must be after start time {i}'})
        if start_times[i].minute != end_times[i].minute and start_times[i].minute != end_times[i].replace(minute=(end_times[i].minute+30)%60).minute:
            raise serializers.ValidationError({'error':f'start time {i} and end time {i} must be in the same or after 30 minutes'})
        for j in range(len_start):
            if start_times[i] == start_times[j] and i != j :
                raise serializers.ValidationError({'error':f'there is time conflicts bettween {i} and {j}'})
            if start_times[i] > start_times[j] and start_times[i] < end_times[j]:
                raise serializers.ValidationError({'error':f'there is time conflicts bettween {i} and {j}'})

def prepare_consluting(validated_data,expert,update):
    con_list = validated_data.pop('expert_conslutings')

    if update:
        expert_cons_list = list(ExpertConsluting.objects.prefetch_related('consulting').
                                filter(consulting__title__in = con_list,expert=expert).
                                values_list('consulting__title',flat=True))
        for item in expert_cons_list:
            if item in con_list:
                con_list.remove(item)

    query_set_list = list(Consluting.objects.filter(title__in = con_list).all())
    for item in query_set_list:
        if item.title in con_list:
            con_list.remove(item.title)
    return (con_list,query_set_list)