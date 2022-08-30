FROM python:3.9

WORKDIR /usr/src/fgstest

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py importcity

EXPOSE 8000

