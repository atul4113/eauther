#!/usr/bin/env python
import os
import sys

from lorepo.boot import fix_path
fix_path()
print(fix_path())

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from djangae.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

# #!/usr/bin/env python
# """Django's command-line utility for administrative tasks."""
# import os
# import sys
# import io
# import environ
#
# ##env = environ.Env()
# # env.read_env(io.StringIO(os.environ.get("user_service_settings", None)))
# env = environ.Env()
#
#
# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)
#
#
# if __name__ == "__main__":
#     main()
