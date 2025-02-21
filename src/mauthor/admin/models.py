from django.db import models

class AdminLog(models.Model):
    '''
    Used to record operations on entities in database.
    entity - string describing the modified entity
    key - id of the entity
    description - what has been done with the entity
    identifier - custom identifier to easily find a group of operations
    
    For example if you perform fix db a sample AdminLog entity may be:
    entity='Content'
    key=content.id
    description='Is_deleted set to True if space in deleted'
    identifier='DELETE_CONTENT_FROM_DELETED_SPACE'
    '''
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    entity = models.CharField(max_length=100)
    key = models.IntegerField()
    description = models.TextField()
    identifier = models.CharField(max_length=500)