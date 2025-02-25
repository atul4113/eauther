from google.auth import app_engine



def mock_get_application_id():
    try:
        application_id = app_engine.get_project_id()
    except Exception:
        # this is a workaround for running unit tests, where no GAE server is running
        application_id = 'ealpha-test-application'

    return application_id
