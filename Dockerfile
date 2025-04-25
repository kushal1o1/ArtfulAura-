FROM python:latest


WORKDIR /artfulaura


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


ENV DJANGO_SETTINGS_MODULE=AAStore.settings

ENV PYTHONUNBUFFERED=1

WORKDIR /artfulaura/AA+MERGE

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

