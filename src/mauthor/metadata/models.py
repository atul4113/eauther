from django.db import models
from lorepo.spaces.models import Space
from lorepo.mycontent.models import Content


class DefinitionType(object):
    SHORT_TEXT = 0
    LONG_TEXT = 1
    SELECT = 2

    names = {
        SHORT_TEXT: 'short_text',
        LONG_TEXT: 'long_text',
        SELECT: 'select'
    }

    @staticmethod
    def get_name(status):
        return DefinitionType.names[status]

class Definition(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    field_type = models.IntegerField(choices=[(DefinitionType.SHORT_TEXT, 'Short text'), (DefinitionType.LONG_TEXT, 'Long text'), (DefinitionType.SELECT, 'Select')], default=1)
    name = models.CharField(max_length=255)
    description = models.TextField()
    value = models.TextField()
    order = models.IntegerField()

class PageMetadata(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    page_id = models.CharField(max_length=20)
    is_enabled = models.BooleanField(default=True)
    
    title = models.CharField(max_length=200)
    tags = models.TextField(max_length=1024, null=True, blank=True, default='')
    description = models.TextField(max_length=1024, null=True, blank=True, default='')
    short_description = models.TextField(null=True, blank=True, default='')

    def __str__(self):
        return "<PageMetadata: content=%s, page_id=%s>" % (self.content.id, self.page_id)

    def __repr__(self):
        return self.__str__()

class MetadataValue(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    field_type = models.IntegerField(choices=[(DefinitionType.SHORT_TEXT, 'Short text'), (DefinitionType.LONG_TEXT, 'Long text'), (DefinitionType.SELECT, 'Select')], default=1)
    name = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    value = models.TextField(default="", blank=True)
    order = models.IntegerField()
    entered_value = models.TextField(default="", blank=True)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    page = models.ForeignKey(PageMetadata, null=True, default=None, on_delete=models.DO_NOTHING)
    is_enabled = models.BooleanField(default=True)

    def as_xml_node(self, document):
        element = document.createElement('metadata-value')
        element.setAttribute('field-type', str(self.field_type))
        element.setAttribute('name', self.name)
        element.setAttribute('description', self.description)
        element.setAttribute('value', self.value)
        element.setAttribute('order', str(self.order))
        entered_value = document.createTextNode(self.entered_value)
        element.appendChild(entered_value)
        return element

    def from_xml_node(self, node):
        self.field_type = node.getAttribute('field-type')
        self.name = node.getAttribute('name')
        self.description = node.getAttribute('description')
        self.value = node.getAttribute('value')
        self.order = node.getAttribute('order')
        self.entered_value = getText(node.childNodes)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)