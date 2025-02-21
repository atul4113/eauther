# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Label(models.Model):
    """
    Etykieta którą można przypisać do contentu. Służy do grupowania
    """
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    
    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title
