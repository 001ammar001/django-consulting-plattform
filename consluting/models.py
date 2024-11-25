from django.db import models
from django.conf import settings
from .validators import validate_date

User = settings.AUTH_USER_MODEL

class Wallet(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,unique=True)
    account = models.IntegerField(default=10000)

class Consluting(models.Model):
    title = models.CharField(max_length=255,unique=True)

    def __str__(self) -> str:
        return self.title

class Expert(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,unique=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    price = models.IntegerField(default=1000)
    image = models.ImageField(upload_to='images',null=True,blank=True)

class ExpertConsluting(models.Model):
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='conslutings')
    consulting = models.ForeignKey(Consluting,on_delete=models.PROTECT)

    class Meta:
        unique_together=[['expert','consulting']]

class Vote(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='votes')
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='votes')
    rate = models.DecimalField(max_digits=2,decimal_places=1)

    class Meta:
        unique_together = [['user','expert']]

class Experince(models.Model):
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='experinces')
    title = models.CharField(max_length=255)
    description = models.TextField()

class FavoriteExpert(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='favorites')
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user','expert']]

class ChatRoom(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='rooms')
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='rooms')
    
    class Meta:
        unique_together = [['user','expert']]

class ChatMessage(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='messages')
    chat_room = models.ForeignKey(ChatRoom,on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

class FreeDay(models.Model):
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='free_days')
    date = models.DateField(validators=[validate_date])

    class Meta:
        unique_together = ['expert','date']

class FreeTime(models.Model):
    free_day = models.ForeignKey(FreeDay,on_delete=models.CASCADE,related_name='free_times')
    start_time = models.TimeField()

class WorkDay(models.Model):
    expert = models.ForeignKey(Expert,on_delete=models.CASCADE,related_name='working_days')
    date = models.DateField(validators=[validate_date])

    class Meta:
        unique_together = ['expert','date']

class WorkTime(models.Model):
    work_day = models.ForeignKey(WorkDay,on_delete=models.CASCADE,related_name='work_times') 
    start_time = models.TimeField()
    user = models.ForeignKey(User,on_delete=models.PROTECT,related_name='booked_times')