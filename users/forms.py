from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email")
