import datetime
from django.template import loader
from django.template.loader import render_to_string
from src.lorepo.filestorage.models import FileStorage
from django.template.context import Context
from src.lorepo.mycontent.models import Content
from src.lorepo.spaces.util import get_private_space_for_user
from src.lorepo.mycontent.service import add_content_to_space

def render_lesson(user, name, pages, server_name):
    now = datetime.datetime.now()
    # template = loader.get_template('pdfimport/initdata/page_with_texts.xml')
    page_files = []
    for page in pages:
        contents = str(render_to_string('pdfimport/initdata/page_with_texts.xml', {'page': page}))

        page_file = FileStorage(
                           created_date = now,
                           modified_date = now,
                           content_type = "text/xml",
                           contents = contents,
                           owner = user)
        page_file.save()
        page_files.append(page_file)
        
    params = {'pages' : page_files,
              'server_name': server_name}
    t = loader.get_template('pdfimport/initdata/content.xml')
    c = Context(params)
    contents = t.render(c)

    contentFile = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = contents,
                            owner = user)
    contentFile.version = 1
    contentFile.save()

    content = Content(
                    title='Pdf import: %s' % name,
                    tags='',
                    description='Lesson imported from pdf', 
                    short_description='',
                    created_date = now, 
                    modified_date = now, 
                    author = user,
                    file = contentFile,
                    icon_href = None)

    content.add_title_to_xml()
    content.save()
    contentFile.history_for = content
    contentFile.save()
    
    space = get_private_space_for_user(user)
    add_content_to_space(content, space)
    return content
