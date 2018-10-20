FROM python:3.4-alpine
COPY requirements.txt /
RUN pip install -r requirements.txt
ENV PYTHONPATH .
COPY . /
WORKDIR /

CMD ["python", "/src/dl/flaskapp/transactions/transactions_app.py"]