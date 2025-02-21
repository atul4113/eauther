from config import HOST


def send_error_message(user_id, pdf_name='', traceback=''):
    from libraries import fetch
    data = {
        'user_id': user_id,
        'traceback': traceback,
        'pdf_name': pdf_name
    }
    fetch.post_as_admin('%s/pdfimport/api/error_message/exception' % HOST, data)
