from django.contrib.auth.models import User
from django.db import models


class UserFeedback(models.Model):
    created_date = models.DateTimeField()
    content = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.content
