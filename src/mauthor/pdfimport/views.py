from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from src.libraries.utility.decorators import backend
from src.libraries.utility.queues import trigger_backend_task
from .forms import PDFUploadForm
from src.lorepo.filestorage.models import UploadedFile
from src.libraries.utility.environment import get_versioned_module
from pdfminer.pdfpage import PDFPage
from src.lorepo.filestorage.utils import get_reader
from django.contrib.auth.models import User
from .api import send_import_failure_notification
import logging
MAX_PDF_SIZE = 53 * 1024 * 1024
MAX_PAGES = 100




@login_required
def upload(request, space_id, pdf_id=None):
    """
    Handles PDF file uploads and triggers a background task for processing.
    """
    form = None
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded file to the storage backend
            uploaded_file = request.FILES['file']
            file_name = default_storage.save(f'pdf_uploads/{uploaded_file.name}', uploaded_file)

            # Create a new PDFModel instance
            model = form.save(commit=False)
            model.owner = request.user
            model.content_type = uploaded_file.content_type
            model.filename = uploaded_file.name
            model.file_path = file_name  # Store the file path in the model
            model.save()

            # Trigger a background task for PDF processing
            parameters = {
                "file_name": uploaded_file.name,
                "space_id": space_id,
                "user_id": request.user.id,
                "file_id": model.id,
                "file_path": file_name,  # Pass the file path to the background task
            }
            trigger_backend_task(
                '/pdfimport/upload/check_pdf',
                target=get_versioned_module('download'),
                queue_name='download',
                params=parameters
            )

            # Notify the user
            messages.info(request, 'PDF import will run in the background. You will be notified by email about the result.')
            return redirect('/mycontent')

    # If not a POST request, initialize the form
    if form is None:
        form = PDFUploadForm()

    # Render the upload template
    return render(request, 'pdfimport/upload.html', {
        'form': form,
        'pdf_id': pdf_id,
    })


@backend
def check_pdf_async(request):
    file_id = request.POST.get('file_id')
    file_model = get_object_or_404(UploadedFile, id=file_id)
    reader = get_reader(file_model)
    user_id = request.POST.get('user_id')

    if not __check_pages_limit(PDFPage.get_pages(reader)):
        logging.error("To many pages in pdf with id: %s" % file_id)
        user = get_object_or_404(User, pk=user_id)
        send_import_failure_notification(user, request.POST.get('file_name'), path='pdfimport/to_many_pages.txt')
        return HttpResponse("OK")

    space_id = request.POST.get('space_id')
    parameters = {
        "file_name": request.POST.get('file_name')
    }
    trigger_backend_task('/gce/import_pdf/%s/%s/%s' % (space_id, user_id, file_id), target=get_versioned_module('gce-backend'), queue_name='gce-backend', params=parameters)
    return HttpResponse("OK")


def __check_pages_limit(pdf_page):
    for index, page in enumerate(pdf_page):
        if index + 1 > MAX_PAGES:
            return False
    return True