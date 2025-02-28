import os
import sys
import logging
from django.core.management import execute_from_command_line

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import os
from google.auth import load_credentials_from_file

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/key.json"

# Test loading credentials
try:
    credentials, project = load_credentials_from_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    print(f"Credentials loaded successfully for project: {project}")
except Exception as e:
    print(f"Error loading credentials: {e}")

# import psycopg2
#
# # Define connection parameters
# conn_params = {
#     'dbname': 'myproject',
#     'user': 'test_user',
#     'password': 'test#123',
#     'host': 'localhost',
#     'port': 5432
# }
#
# try:
#     # Establish connection
#     conn = psycopg2.connect(**conn_params)
#     print("✅ Database connection successful!")
#
#     # Create a cursor
#     cur = conn.cursor()
#     cur.execute("SELECT version();")
#     print("PostgreSQL version:", cur.fetchone())
#
#     # Close the connection
#     cur.close()
#     conn.close()
# except Exception as e:
#     print(f"❌ Database connection failed: {e}")

def main():
    try:
        # Set the default Django settings module
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

        # Log the environment settings
        logging.info(f"DJANGO_SETTINGS_MODULE set to: {os.environ['DJANGO_SETTINGS_MODULE']}")

        # Execute the command line arguments
        execute_from_command_line(sys.argv)
    except Exception as e:
        # Log any exceptions that occur
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()