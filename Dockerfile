FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app /app/app
COPY ./requirements.txt /app
COPY ./alembic.ini /app
COPY ./logging.conf /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80
EXPOSE 443

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]