from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/gce/import_pdf/<space_id>/<user_id>/<file_id>', methods=['POST'])
def import_pdf(space_id, user_id, file_id):
    from .pdf_import import parser_task

    try:
        parser_task.import_pdf(request, space_id, user_id, file_id)
    except Exception as err:
        import traceback
        logging.exception("Parsing Error: %s" % str(err))
        logging.exception(traceback.format_exc())
        from .pdf_import.utils import messages
        messages.send_error_message(user_id, pdf_name=request.form["file_name"], traceback=traceback.format_exc())
    return "OK"


@app.route('/_ah/health')
def health_check():
    return "OK"

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8002, debug=True)