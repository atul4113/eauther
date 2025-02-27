import json
import logging
import src.cloudstorage as gcs
import uuid

from django.contrib.auth.models import User
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.mycontent.models import Content
from src.mauthor.lessons_parsers.property_changer.util import Logger
from src.mauthor.utility.db_safe_iterator import safe_iterate
from src.lorepo.filestorage.utils import create_new_version, build_retry_params
from src.settings import get_bucket_name
from lxml import etree


class DescriptorsCleaner(object):
    CHANGER_USERNAME = "cleaner"

    def __init__(self, user_id, space_id, config):
        self.user_id = user_id
        self.space_id = space_id
        self.config = config
        self.logger = None
        self.gcs_path = "%s/lesson-property-parser/remove_descriptor/%s/%s/%d" % (get_bucket_name('export-packages'), user_id, space_id, uuid.uuid4().int)
        self.changer_user = get_object_or_none(User, username=self.CHANGER_USERNAME)
        if self.changer_user is None:
            raise Exception("Can't find user for changer")

    def clean(self):
        with gcs.open(self.gcs_path, mode='w', content_type="text/html", retry_params=build_retry_params()) as gcs_file:
            self.logger = Logger(json.dumps(self.config), gcs_file)
            self.logger.add_log(action="STARTED",
                                title="Started editing",
                                type="INFO")

            try:
                if self.config["is_process_all_lessons"]:
                    contents = Content.objects.filter(spaces=str(self.space_id), is_deleted=False, content_type=1)
                    self._clear_from_all_lessons(contents)
                else:
                    lesson_id = self.config["lesson_id"]
                    self._clear_from_one_lesson(lesson_id)
            except Exception as e:
                import traceback
                self.logger.add_log(action='STOP',
                                    type='Error',
                                    message='%s,%s' % (e, traceback.format_exc()))

    def _clear_from_one_lesson(self, lesson_id):
        contents = Content.objects.filter(pk=lesson_id, spaces=str(self.space_id), is_deleted=-False, content_type=1)
        self._clear_from_all_lessons(contents)

    def _clear_from_all_lessons(self, contents):
        for batch in safe_iterate(contents):
            for content in batch:
                self._clear_lesson(content)

    def _clear_lesson(self, content):
        self.logger.add_log(action="WORKING_ON_LESSON",
                            lesson_id=content.id,
                            title=content.title,
                            version_number=content.file.version,
                            type="INFO")
        logging.info(
            'LESSON_PARSER,\"%s\",%d,%d' % (content.title, int(content.id), content.file.version))

        editing = content.who_is_editing()
        if editing is not None:
            self.logger.add_log(action="PASSED",
                                lesson_id=content.id,
                                title=content.title,
                                version_number=content.file.version,
                                type="WARNING",
                                message="Lesson is editing")
        else:
            content.set_user_is_editing(self.changer_user)
            try:
                new_version = create_new_version(content.file, self.changer_user, False, 'descriptor_cleaner')
                self.logger.add_log(action="CREATED NEW VERSION")

                lesson_content = new_version.contents
                addon_descriptor = self.config["addon_descriptor"]
                is_descriptor_found = lesson_content.decode('UTF-8').find('addonId="' + addon_descriptor.decode('UTF-8'))

                if is_descriptor_found > 0:
                    self.logger.add_log(action="FOUND_DESCRIPTOR",
                                        lesson_id=content.id,
                                        title=content.title,
                                        version_number=content.file.version,
                                        message=addon_descriptor,
                                        type="INFO")

                    lesson_content = self._process_lesson_content(lesson_content, addon_descriptor)

                    new_version.contents = lesson_content
                    new_version.save()

                    content.file = new_version
                    content.save()
                    self.logger.add_log(action="LESSON_SAVED")
                else:
                    self.logger.add_log(action="NOT_FOUND_DESCRIPTOR",
                                        lesson_id=content.id,
                                        title=content.title,
                                        version_number=content.file.version,
                                        message=addon_descriptor,
                                        type="INFO")
            except Exception as e:
                import traceback
                self.logger.add_log(action='STOP', type='Error', message='%s,%s' % (e, traceback.format_exc()))
            finally:
                content.stop_editing(self.changer_user)

    def _process_lesson_content(self, lesson_content, addon_descriptor):
        xml_document = etree.fromstring(lesson_content)
        for xml_child_node in xml_document:
            if xml_child_node.tag == 'addons':
                for xml_addon_descriptor in xml_child_node:
                    if xml_addon_descriptor.attrib['addonId'] == addon_descriptor:
                        xml_child_node.remove(xml_addon_descriptor)
        return etree.tostring(xml_document, xml_declaration=True,   encoding="utf-8")

