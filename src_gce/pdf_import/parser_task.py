from settings import get_bucket_name
from .utils import zip, messages
from subprocess import CalledProcessError
from libraries import storage
import logging
import tempfile
import urllib.request, urllib.error, urllib.parse
import uuid

from pdf_import import parser
from config import HOST
from libraries import fetch


def import_pdf(request, space_id, user_id, file_id):
    tempdirname = tempfile.mkdtemp()
    try:
        _import_pdf(tempdirname, request, space_id, user_id, file_id)
    except:
        raise
    finally:
        import shutil
        shutil.rmtree(tempdirname)


def _import_pdf(tempdirname, request, space_id, user_id, file_id):
    def escape_pdf_name(name):

        available_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ. "

        new_name = [char for char in name if char in available_chars]

        return ''.join(new_name)

    try:
        pdf_name = escape_pdf_name(request.form["file_name"])
        if len(pdf_name) == len('.pdf'):
            pdf_name = "LessonFromPDF.pdf"
    except Exception:
        logging.error("Post don't have file name")
        messages.send_error_message(user_id, traceback="Post don't have file name")
        return "OK"

    logging.info("%s: Working on pdf, HOST: %s" % (pdf_name, HOST))

    pdf_file_fetch = urllib.request.urlopen("%s/file/serve/%s" % (HOST, file_id), timeout=30)
    logging.info("%s: Temp dir name: %s" % (pdf_name, tempdirname))
    with open("%s/%s" % (tempdirname, pdf_name), 'wb') as output:
        output.write(pdf_file_fetch.read())

    try:
        parser.parse_pdf("%s/" % tempdirname, pdf_name)
    except CalledProcessError as err:
        import traceback
        logging.exception("Parsing Error: %s" % str(err))
        logging.exception(traceback.format_exc())
        logging.exception(err.output)
        messages.send_error_message(user_id, pdf_name=pdf_name, traceback="Process err: %s, traceback: %s" % (err.output, traceback.format_exc()))
        return "OK"

    zip.zip_lesson(tempdirname)

    unique_id = str(uuid.uuid4().int)
    storage.upload_file_by_path(tempdirname + "/zip_file.zip", get_bucket_name('imported-resources')[1:], "gce_exchange/import_pdf/%s/%s/%s" % (space_id, user_id, unique_id))

    fetch.get_as_admin("%s/pdfimport/api/gce_callback/%s/%s/%s" % (HOST, space_id, user_id, unique_id)) #fetch as admin

    return "OK"
