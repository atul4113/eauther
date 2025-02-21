from django.shortcuts import get_object_or_404, render
from lorepo.mycontent.models import Content
from mauthor.exchange_narration.model import ExportNarration, ExportedNarration
from django.contrib.auth.decorators import login_required

def _find_version(previous_exports, content):

    for pe in previous_exports:
        export_file = pe.export_file
        if export_file.version == content.file.version:
            return export_file

    return False

@login_required
def export(request, content_id, export_type):
    content = Content.get_cached_or_404(id = content_id)

    previous_exports = ExportedNarration.objects.filter(content = content)
    previous_exports_filtered = [pe for pe in previous_exports if pe.export_file.content_type.split('/')[1] == export_type]
    export_file_for_content_version = _find_version(previous_exports_filtered, content)
    export_narration = ExportNarration(content)

    if len(previous_exports_filtered) == 0 or not export_file_for_content_version:
        export_narration.set_export_type(export_type)
        export_narration.set_pages()
        export_narration.set_narrations()

        if export_type == 'html':
            export_file = export_narration.create_html(request.user)
        elif export_type == 'csv':
            export_file = export_narration.create_csv(request.user)

        export_file.version = content.file.version
        export_file.save()
        exported_narration = ExportedNarration(content = content, export_file = export_file)
        exported_narration.save()
    else:
        export_file = export_file_for_content_version
        if export_type == 'html':
            export_narration.recreate_header_html(export_file)
        elif export_type == 'csv':
            export_narration.recreate_header_csv(export_file)

    return render(request, 'exchange_narration/success_export.html', { 'export_file' : export_file, 'export_type' : export_type })