FROM python:3.10-slim

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8050

#COPY . /app/
CMD gunicorn -b :8050 --preload --forwarded-allow-ips="0.0.0.0" --pythonpath /app --workers=2 main:server