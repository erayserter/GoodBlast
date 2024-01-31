FROM python:3.11-alpine as web

# Setting up the work directory
WORKDIR /home/app/

# Preventing python from writing
# pyc to docker container
ENV PYTHONDONTWRITEBYTECODE 1

# Flushing out python buffer
ENV PYTHONUNBUFFERED 1

# Copying requirement file
COPY ./requirements.txt ./

# Upgrading pip version
RUN pip install --upgrade pip

# Installing dependencies
RUN pip install -r ./requirements.txt

# Copying all the files in our project
COPY . .
