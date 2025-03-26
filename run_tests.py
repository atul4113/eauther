import configparser
import io
import os
import subprocess
import sys
import imp


REQUIRED_DJANGO_VERSION = (1, 8, 12, 'final', 0)


# While executing tests there should be only sys paths which target mAuthor project.
# Containing a path which targets another project can generate weird problems.
SYS_PATHS_TO_REMOVE = [
    "mcurriculum",
    "website",
    "django",
]


def log(priority, message):
    print(("[{}] {}".format(priority, message)))


def log_info_message(message):
    log('INFO', message)


def empty_method(*args, **kwargs):
    pass


def _get_directory():
    return os.path.dirname(os.path.realpath(__file__))


def check_dependencies():
    """
    Check if dependencies required to run test script are installed.
    If a dependency is not installed then throw an error.

    Raises:
        Exception: If the dependency is not installed.
    """
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

    with open("{}/requirements-test.txt".format(_get_directory()), "r") as req_file:
        req_dep = req_file.read()

        required_packages = [r.decode().split('==')[0] for r in req_dep.split()]

        for required_package in required_packages:
            if required_package not in installed_packages:
                raise Exception("Tests need '{}' dependency. Run 'pip install -r requirements-tests.txt'.".format(required_package))


def check_django_version():
    try:
        import django
    except Exception:
        raise Exception("Error while importing django. Check if all dependencies are correctly installed")

    if not (django.VERSION == REQUIRED_DJANGO_VERSION):
        raise Exception("mAuthor requires django in {} version but found {}. Check python packages if correct version is installed.".format(REQUIRED_DJANGO_VERSION, django.VERSION))


def check_app_engine_correctly_imported():
    try:
        imp.find_module('appcfg')
    except:
        raise Exception("Path to google app engine sdk is not configured correctly.")


def get_build_properties():
    """
    Open build.properties file and return a ConfigParser object. The properties are in ANT_CONFIG section.
    Returns:
        ConfigParser: always
    """
    with open("{}/build.properties".format(_get_directory()), "r") as properties_file:
        properties_data = properties_file.read()

    config = """[ANT_CONFIG]
{}
        """.format(properties_data)

    config_file = io.StringIO(config)

    config = configparser.RawConfigParser()
    config.readfp(config_file)

    return config


def configure_environment():
    """
        Set correct python path before executing tests.
    """
    check_dependencies()

    # Open build.properties and get path to the google app engine SDK
    build_properties = get_build_properties()

    appcfg_path = build_properties.get('ANT_CONFIG', 'appcfg.path')
    appcfg_dir = os.path.dirname(appcfg_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    root_path = os.path.join(base_dir, 'src')
    site_packages_path = os.path.join(root_path, 'sitepackages')

    log_info_message("GOOGLE APP ENGINE DIR: {}".format(appcfg_dir))

    # Add to sys path appengine dir and check if is correct
    sys.path.append(appcfg_dir)
    check_app_engine_correctly_imported()

    # Load paths from appcfg for tests.
    import appcfg
    sys.path = sys.path + appcfg._PATHS._script_to_paths['dev_appserver.py']

    # Remove from the sys path elements which can collide with new appended elements
    for path_to_remove in SYS_PATHS_TO_REMOVE:
        sys.path = [path for path in sys.path if path.find(path_to_remove) == -1]

    sys.path.append(root_path)
    sys.path.append(site_packages_path)
    check_django_version()  # We need to check django version there because now it should be visible


def fast_run_tests():
    """
    Try to mock django method which removes data from database. It should work faster than standard test.
    """
    log_info_message("Running tests with cleaning optimization")
    from django.test import TransactionTestCase
    from django.test import TestCase
    from django.core.management import call_command

    from mock import patch

    def call_command_mock(command, *args, **kwargs):
        if command != 'migrate':
            call_command(command, *args, **kwargs)

    with patch.object(TransactionTestCase, '_fixture_teardown', empty_method), \
         patch.object(TestCase, '_fixture_teardown', empty_method), \
         patch('django.core.management.call_command', call_command_mock):   # It takes ~2sec, but we dont need a migrations
        import pytest
        pytest.main(sys.argv[1:])


def standard_run():
    """
    Run tests without optimizations
    """
    import pytest
    pytest.main(sys.argv[1:])


def execute_src():
    """
        Execute tests for django backend
    """
    configure_environment()

    # Run pytest with arguments provided to the script

    if "--fast_run" in sys.argv:
        sys.argv.remove("--fast_run")
        fast_run_tests()
    else:
        standard_run()

if __name__ == "__main__":
    execute_src()