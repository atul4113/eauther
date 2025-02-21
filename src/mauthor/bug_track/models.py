from django.db import models
from django.contrib.auth.models import User
from lorepo.mycontent.models import Content

class Bug(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    
    def __unicode__(self):
        return self.title