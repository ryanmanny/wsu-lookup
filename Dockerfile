FROM python:3.10-alpine

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY main.py .
COPY data data
COPY src src

ENTRYPOINT ["python", "main.py"]
