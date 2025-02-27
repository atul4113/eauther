from src.libraries.utility import cacheproxy as cache
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.filestorage.utils import create_new_version
from src.lorepo.mycontent.lesson.update_content_template_task import UpdateContentBasingOnTemplate
from src.lorepo.mycontent.models import UpdateTemplateStatus
from lxml import etree


def update_content_template(content, user, preferences, template_content=None):
    '''Updates content with current template. Return codes:
    0 - template updated
    1 - content had no template
    2 - content is currently edited
    3 - template is currently edited
    '''
    comment = 'template_change'

    if content.who_is_editing() is not None:
        return UpdateTemplateStatus.CONTENT_CURRENTLY_EDITED
    if not template_content:
        template_content = content.get_template()
        comment = 'template_update'
    if not template_content:
        return UpdateTemplateStatus.NO_TEMPLATE
    if template_content.who_is_editing() is not None:
        return UpdateTemplateStatus.TEMPLATE_CURRENTLY_EDITED

    newest_template_file = FileStorage.objects.filter(history_for__id = template_content.id).order_by('-version')[0]
    template_contents_xml = newest_template_file.contents
    content.file = create_new_version(content.file, user, comment=comment, shallow=True)
    content.save()
    content_main_xml = content.file.contents

    task = UpdateContentBasingOnTemplate(content_main_xml, template_contents_xml, preferences, newest_template_file.id)
    status, content_root_xml = task.execute()
    if status:
        content.file.contents = etree.tostring(content_root_xml, encoding='UTF-8')
        content.file.save()
        cache.set("content_template_%s" % content.id, template_content, 60 * 60 * 24)
        return UpdateTemplateStatus.UPDATED