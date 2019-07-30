FROM python:3.7.3-stretch

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

RUN mv .aws /root/.

CMD ["python", "api/app.py"]
