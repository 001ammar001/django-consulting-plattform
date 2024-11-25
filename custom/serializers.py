from rest_framework_simplejwt.tokens import RefreshToken
from djoser.serializers import UserCreateSerializer as BaseUserCreate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as TOB, TokenVerifySerializer as TOV
from djoser.conf import settings

class UserCreatSerializer(BaseUserCreate):
    class Meta(BaseUserCreate.Meta):
        fields = ['id','username','email','password','first_name','last_name','is_expert']

    def to_representation(self, instance):
        user_tokens = RefreshToken.for_user(instance)
        tokens = {'refresh':str(user_tokens),'accsess':str(user_tokens.access_token)}
        data = {'id':instance.id,'tokens':tokens}
        return data

class TokenObtainPairSerializer(TOB):

    default_error_messages = {
        "no_active_account": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
    }

    
class TokenVerifySerializer(TOV):
    
    def validate(self, attrs):
        print('here')
        #return super().validate(attrs)
        return 'a'
    