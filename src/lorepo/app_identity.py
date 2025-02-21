from google.appengine.api.app_identity import get_application_id


def mock_get_application_id():
    try:
        application_id = get_application_id()
    except Exception:
        # this is a workaround for running unit tests, where no GAE server is running
        application_id = 'ealpha-test-application'

    return application_id
