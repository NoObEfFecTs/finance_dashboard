FROM python:slim

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY . /app/
CMD gunicorn --bind=0.0.0.0:8050 --preload --pythonpath /app --workers=2 main:server
