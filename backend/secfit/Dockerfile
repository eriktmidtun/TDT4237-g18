# Use the official Python image from the Docker Hub
FROM python:3.8.5-slim

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Make a new directory to put our code in.
RUN mkdir /code

# Change the working directory. 
# Every command after this will be run from the /code directory.
WORKDIR /code

# Copy the of the code. 
COPY . /code/

# Add sqlite3 to enable dbshell command for managing the database
RUN apt-get update -y && apt-get install sqlite3 -y

# Upgrade pip
RUN pip install --upgrade pip

# Install the requirements.
RUN pip install -r requirements.txt

# Import groupid environment variable
ENV GROUPID=${GROUPID}

# Initialize Django
RUN python manage.py migrate

# Import credential variables
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_EMAIL

# Create superuser
RUN DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME} \
    DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD} \
    DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL} \
    python manage.py createsuperuser --noinput || \
    echo "WARNING: This error is ignored as it most likely is 'That username is already taken.'" \
    && echo "If you wish to alter the user credentials, then delete the user first."

# Create some exercises from seed data
RUN python manage.py loaddata seed.json

# Run wsgi server with gunicorn
CMD ["gunicorn", "secfit.wsgi", "--log-file", "-", "-b", "0.0.0.0:8000"]
