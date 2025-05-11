from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrong_password_count = models.IntegerField(default=0)
    wrong_password_timeout = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} \nPassword Count: {self.wrong_password_count}"