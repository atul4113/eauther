import os
import sys
# import logging
from django.core.management import execute_from_command_line

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# def main():
#     try:
#         # Set the default Django settings module
#         os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
#
#         # Log the environment settings
#         # logging.info(f"DJANGO_SETTINGS_MODULE set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
#
#         # Execute the command line arguments
#         execute_from_command_line(sys.argv)
#     except Exception as e:
#         print(e)
#         # Log any exceptions that occur
#         # logging.error(f"An error occurred: {e}", exc_info=True)
#         sys.exit(1)
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# import os
# import sys
#
# if __name__ == '__main__':
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#
#     from djangae.sandbox import start_emulators, stop_emulators
#
#     try:
#         # Start all emulators, persisting data if we're not testing
#         start_emulators(persist_data="test" not in sys.argv)
#         execute_from_command_line(sys.argv)
#     finally:
#         # Stop all emulators
#         stop_emulators()