FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies with all required packages for mysqlclient
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        python3-dev \
        # MySQL/MariaDB dependencies
        default-libmysqlclient-dev \
        pkg-config \
        libssl-dev \
        libmariadb-dev-compat \
        libmariadb-dev \
        # PostgreSQL dependencies
        libpq-dev \
        postgresql-client \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /code
# RUN pip install --no-cache-dir mysqlclient==2.2.7 --only-binary :all:
# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary
# Copy custom packages
COPY ./custom_packages/rest_framework_docs /usr/local/lib/python3.10/site-packages/rest_framework_docs
COPY ./custom_packages/rest_framework_jwt /usr/local/lib/python3.10/site-packages/rest_framework_jwt

# Copy project files
COPY . .

# Run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]