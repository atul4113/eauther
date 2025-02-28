import traceback

from src import settings
from django.http.response import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.template.context import Context
from django.views.generic.base import View
import logging
from src.libraries.utility.decorators import BackendMixin
from src.libraries.utility.helpers import get_object_or_none
from src.libraries.utility.queues import trigger_backend_task
from src.lorepo.exchange.models import ExportWOMIPages, ExportWOMIPage
from src.lorepo.exchange.views import exported_file
from src.lorepo.merger.models import ContentMerger
from src.lorepo.mycontent.util import clean_content_assets
from src.lorepo.public.util import send_message
from src.mauthor.metadata.util import copy_page_metadata

_no_value = object()


class ExportWOMIPagesAsyncView(BackendMixin, View):
    pages = []
    commons = []
    export = _no_value
    error_mail = 'exchange/womi-pages-error.txt'
    success_mail = 'exchange/womi-pages-confirmation.txt'

    def post(self, request, womi_pages_id):
        self.export = get_object_or_none(ExportWOMIPages, pk=womi_pages_id)

        if self.export is not None and self.export is not _no_value:
            if not self.export.in_progress:
                self.export.in_progress = True
                self.export.save()

                try:
                    self.get_pages()

                    self.export.commons_indexes = self._get_entities_indexes(self.commons)
                    self.export.pages_count = len(self.pages)
                    self.export.save()

                    self.start()

                except Exception as e:
                    logging.error('Exception')
                    logging.error(e.message)
                    exception_traceback = traceback.format_exc()
                    logging.error(exception_traceback)
                    self.finish(success=False, exception_traceback=exception_traceback)
            else:
                pages_exports_count = ExportWOMIPage.objects.filter(pages_export=self.export, is_finished=True).count()
                success_pages_exports_count = ExportWOMIPage.objects\
                    .filter(pages_export=self.export, is_finished=True, is_success=True).count()

                if pages_exports_count == self.export.pages_count:
                    if success_pages_exports_count == self.export.pages_count:
                        self.finish(success=True)
                    else:
                        self.finish(success=False)
                    return HttpResponse('OK')

        return HttpResponseForbidden()

    def get_pages(self):
        merger = ContentMerger(self.export.content)
        self.pages = merger.flat_page_chapter_structure()
        self.commons = merger.common_pages()

    def start(self):
        pages_indexes = self._get_entities_indexes(self.pages)

        for page_idx in pages_indexes:
            page_export = ExportWOMIPage(
                user=self.export.user,
                pages_export=self.export,
                page_index=page_idx
            )
            page_export.save()

            trigger_backend_task('/exchange/export/{}/womi/page_async'.format(page_export.id), queue_name='download')

    def finish(self, success=True, exception_traceback=None):
        self.export.in_progress = False
        self.export.is_success = success
        self.export.traceback = exception_traceback

        self.export.save()

        if success:
            self._send_success_notification()
        else:
            self._send_error_notification()

    def _send_success_notification(self):
        subject = 'Pages from lesson "{}" successfully exported as WOMI'.format(self.export.content.title)
        context = Context({
            'content': self.export.content,
            'user': self.export.user,
            'settings': settings,
            'packages': self.export.sorted_packages
        })
        self._send_notification(subject, context, self.success_mail)

    def _send_error_notification(self):
        subject = 'Exporting pages from lesson "{}" exported as WOMI failed'.format(self.export.content.title)
        context = Context({
            'content': self.export.content,
            'user': self.export.user,
            'settings': settings
        })
        self._send_notification(subject, context, self.error_mail)

    def _send_notification(self, subject, context, template):
        email = loader.get_template(template)
        rendered = email.render(context)
        send_message(settings.SERVER_EMAIL, [self.export.user.email], subject, rendered)

    def _get_entities_indexes(self, entities):
        return [entity.get('index') for entity in entities]


class ExportWOMIPageAsyncView(BackendMixin, View):

    export = _no_value
    error_mail = 'exchange/womi-page-error.txt'

    def post(self, request, womi_page_id):
        self.export = get_object_or_none(ExportWOMIPage, pk=womi_page_id)

        if self.export is not _no_value and self.export is not None:
            try:
                self.export.in_progress = True
                self.export.save()

                self.export.new_content = self.extract_page(self.export.page_index, self.export.pages_export.commons_indexes)
                self.export.save()

                self.export.exported_womi_package = self.export_womi_package()
                self.export.save()

                self.finish()
            except Exception as e:
                logging.error('Exception')
                logging.error(e.message)
                exception_traceback = traceback.format_exc()
                logging.error(exception_traceback)
                self.finish(success=False, exception_traceback=exception_traceback)

            return HttpResponse('OK')

        return HttpResponseForbidden()


    def extract_page(self, page_index, commons_ids):
        merge_lesson = {
            'pages': [page_index],
            'common_pages': commons_ids,
            'content_id': self.export.content.id
        }
        new_content, translated_pages_ids = ContentMerger.create_merged_content(self.export.user, [merge_lesson])
        new_content.title = '{} - page {}'.format(self.export.content.title, (page_index + 1))
        new_content.save()

        clean_content_assets(self.export.user, new_content)

        self.copy_metadata(new_content, translated_pages_ids)
        return new_content

    def copy_metadata(self, new_content, page_translated_ids):
        for content_id, translated_ids in page_translated_ids:
            copy_page_metadata(self.export.content, new_content, translated_ids)

    def export_womi_package(self):
        exported_package = exported_file(self.export.new_content, self.export.user, self.export.pages_export.version, True)
        return exported_package

    def finish(self, success=True, exception_traceback=None):
        self.export.in_progress = False
        self.export.is_success = success
        self.export.is_finished = True
        self.export.traceback = exception_traceback

        self.export.save()

        if not self.export.is_success:
            self._send_error_notification()

    def _send_error_notification(self):
        self.export.in_progress = False
        self.export.is_success = False

        subject = 'Exporting page {} from lesson "{}" exported as WOMI failed'\
            .format((self.export.page_index + 1), self.export.content.title)

        context = Context({
            'content': self.export.content,
            'user': self.export.user,
            'settings': settings
        })
        email = loader.get_template(self.error_mail)
        rendered = email.render(context)
        send_message(settings.SERVER_EMAIL, [self.export.user.email], subject, rendered)
