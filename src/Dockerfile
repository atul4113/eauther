# Dockerfile
FROM python:3.10-slim

# Install Git and clean up cache
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install git+https://github.com/potatolondon/djangae.git@2.0.0rc4#egg=djangae
RUN pip install psycopg2-binary

# Copy only the custom package or files you edited
COPY ./custom_packages/rest_framework_docs /usr/local/lib/python3.10/site-packages/rest_framework_docs
COPY ./custom_packages/rest_framework_jwt /usr/local/lib/python3.10/site-packages/rest_framework_jwt

# Copy project files
COPY . /code/

# Run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
