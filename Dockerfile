FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt /requirements.txt


RUN pip3 install --no-cache-dir -r /requirements.txt \
    && rm -f /requirements.txt

COPY exporter.py /app/exporter.py

CMD ["python3", "exporter.py"]
