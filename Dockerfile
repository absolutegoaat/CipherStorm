FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# create app directory and make it the working dir
RUN mkdir -p /cipherstorm
WORKDIR /cipherstorm

# copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy app
COPY . .

RUN mkdir -p static/images && chmod -R 0777 static/images

EXPOSE 8080

CMD ["python3", "index.py"]
