from django.contrib.auth.models import User
from django.db import models
from lorepo.spaces.models import Space
from lorepo.filestorage.models import UploadedFile

class TicketStatus():
    NEW = 1
    ACCEPTED = 2
    IN_DEVELOPMENT = 3
    CLOSED = 4
    READY = 5

class TicketType():
    BUG = 1
    QUESTION = 2
    REQUEST = 3

class Ticket(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    last_comment_date = models.DateTimeField()
    company = models.ForeignKey(Space, null=True, on_delete=models.DO_NOTHING)
    lesson_url = models.CharField(max_length=500)
    assigned_to = models.ForeignKey(User, null=True, related_name="assignee", on_delete=models.DO_NOTHING)
    ticket_type = models.IntegerField(choices=[(TicketType.BUG, 'Bug'),
                                          (TicketType.QUESTION, 'Question'),
                                          (TicketType.REQUEST, 'Request'),
                                          ], default=1)
    status = models.IntegerField(choices=[(TicketStatus.NEW, 'new'),
                                          (TicketStatus.ACCEPTED, 'accepted'),
                                          (TicketStatus.IN_DEVELOPMENT, 'in development'),
                                          (TicketStatus.CLOSED, 'closed'),
                                          (TicketStatus.CLOSED, 'ready')
                                          ], default=1)

    def __str__(self):
        return self.title

class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def getLastComment(cls, ticket):
        return cls.objects.filter(ticket=ticket).order_by('-created_date')[0]

class TicketAttachment(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING)
    file = models.ForeignKey(UploadedFile, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)