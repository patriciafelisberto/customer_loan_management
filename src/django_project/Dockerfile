FROM python:3

ENV PYTHONUNBUFFERED 1
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

WORKDIR /app

COPY ./src/django_project/requirements.txt ./

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get clean

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]