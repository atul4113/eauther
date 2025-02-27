import json
import uuid
import logging
from xml.dom import minidom

import src.cloudstorage as gcs
from django.conf import settings
from django.contrib.auth.models import User
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.filestorage.utils import create_new_version, build_retry_params
from src.lorepo.mycontent.models import Content
from src.lorepo.public.util import send_message
from src.mauthor.lessons_parsers.property_changer.parsers.parsers import ModuleParserFactory, AddonParser
from src.mauthor.utility.db_safe_iterator import safe_iterate
from .models import PageModel, AddonModel
from src.settings import get_bucket_name
from .util import Logger


class PropertiesChanger(object):
    CHANGER_USERNAME = "changer"

    def __init__(self, user_id, space_id, config):
        self.config = config
        self.space_id = space_id
        self.user_id = user_id
        self.gcs_path = "%s/lesson-property-parser/reports/%s/%s/%d" % (get_bucket_name('export-packages'), user_id, space_id, uuid.uuid4().int)
        self.addon_module_parser_factory = None
        self.logger = None
        self.changer_user = get_object_or_none(User, username=self.CHANGER_USERNAME)
        if self.changer_user is None:
            raise Exception("Can't find user for changer")

    def change(self):
        AddonModel.MODELS = {}
        with gcs.open(self.gcs_path, mode='w', content_type="text/html", retry_params=build_retry_params()) as gcs_file:
            self.logger = Logger(json.dumps(self.config), gcs_file)
            self.logger.add_log(action="STARTED",
                                title="Started editing",
                                type="INFO")

            try:
                contents = Content.objects.filter(spaces=str(self.space_id), content_type=1)
                self.__parse_contents(contents)
            except Exception as e:
                import traceback
                self.logger.add_log(action='STOP',
                                    type='Error',
                                    message='%s,%s' % (e, traceback.format_exc()))
            finally:
                self.__send_notification()

    def __parse_contents(self, contents):
        for batch in safe_iterate(contents):
            for content in batch:
                self.logger.add_log(action="WORKING_ON_LESSON",
                                    title=content.title,
                                    version_number=content.file.version,
                                    lesson_id=content.id,
                                    type="INFO")
                # Add information about parsing to logs.
                logging.info(
                    'LESSON_PARSER,\"%s\",%d,%d' % (content.title, int(content.id), content.file.version))

                self.__parse_content(content)

    def __parse_content(self, content):
        editing = content.who_is_editing()
        if editing is not None:
            self.logger.add_log(action="PASSED",
                                title=content.title,
                                version_number=content.file.version,
                                lesson_id=content.id,
                                type="WARNING",
                                message="Lesson is edited")
        else:
            content.set_user_is_editing(self.changer_user)
            new_version = create_new_version(content.file, self.changer_user, False, 'properties_changer')
            save_content = True
            try:
                pages = minidom.parseString(new_version.contents).getElementsByTagName('page')

                for index, page in enumerate(pages):
                    page_model = PageModel(page, index)
                    self.logger.add_log(action="FOUND_PAGE",
                                        title=page_model.name,
                                        is_common=page_model.is_in_commons,
                                        page_id=page_model.href,
                                        type="INFO",
                                        page_number=page_model.number)

                    is_valid, message = page_model.valid(self.config)
                    if is_valid:
                        page_model.complete_model()
                        self.__parse_page(page_model)
                    else:
                        self.logger.add_log(**message)

            except Exception as e:
                save_content = False
                import traceback
                self.logger.add_log(action='STOP', type='Error', message='%s,%s' % (e, traceback.format_exc()))
            finally:
                if save_content:        # if was exception or error, don't set this version as main version
                    content.file = new_version
                    content.save()
                content.stop_editing(self.changer_user)

    def __send_notification(self):
        user = get_object_or_none(User, pk=self.user_id)
        uploaded_file = UploadedFile(path=self.gcs_path)
        uploaded_file.save()

        url = "%s/file/serve/%s" % (settings.BASE_URL, uploaded_file.id)
        subject = 'Property change has finished'
        send_message(settings.SERVER_EMAIL, [user.email], subject, "Property changer report: %s" % url)

    def __parse_page(self, page_model):
        parser_cls = ModuleParserFactory.get(self.config['addon_name'])
        if parser_cls is None:
            parser_cls = AddonParser

        parser = parser_cls(logger=self.logger)

        self.logger.add_log(action='WORKING_ON_PAGE',
                            type="INFO",
                            page_id=page_model.href)
        changed = parser.parse(self.config, page_model)
        if changed:
            self.logger.add_log(action="SAVING_PAGE",
                                type="INFO",
                                page_id=page_model.href)
            page_model.page.contents = page_model.page_xml.toxml('UTF-8')
            page_model.page.save()

