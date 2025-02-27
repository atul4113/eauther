from django.db import models
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.models import Content


class State(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)
    name = models.CharField(max_length=200)
    rank = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s' % self.name


class StatesSet(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return '%s' % self.name


class StateToSet(models.Model):
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    states_set = models.ForeignKey(StatesSet, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return '%(set)s:%(state)s' % {'state': self.state.name, 'set': self.states_set.name}


class ProjectStatesSet(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    states_set = models.ForeignKey(StatesSet, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return '%(project)s:%(set)s' % {'project': self.project.title, 'set': self.states_set.name}


class ContentState(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=False)

    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return '%(content)s:%(state)s' % {'content': self.content.title, 'state': self.state.name}
