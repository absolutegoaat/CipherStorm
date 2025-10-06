# Use the latest slim Python 3.12 image
FROM python:3.12-slim

# Set environment variables to avoid writing .pyc files and buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a user for security
RUN useradd -m cipherstorm
USER cipherstorm

WORKDIR /cipherstorm  # Best practice to use lowercase directory name

COPY requirements.txt . 
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8080

CMD ["python3", "index.py"]
