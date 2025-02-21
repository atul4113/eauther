from dbindexer.api import register_index
from lorepo.mycontent.models import Content

register_index(Content, {'spaces_path' : 'contains'})