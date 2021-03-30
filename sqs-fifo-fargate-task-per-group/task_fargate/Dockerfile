FROM python:3.7-alpine

WORKDIR /src/app/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python3.7", "app.py"]