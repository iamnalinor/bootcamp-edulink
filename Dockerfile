FROM python:3.12.1-alpine3.19

WORKDIR /app

ENV PYTHONUNBUFFERED=1

STOPSIGNAL SIGKILL

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN ["pybabel", "compile", "-d", "locales/"]
CMD ["python", "-m", "app"]
