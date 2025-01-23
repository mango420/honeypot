FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY honeypot.py /app/
EXPOSE 8080 2222 2121
CMD ["python", "honeypot.py"]
