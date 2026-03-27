FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8001
ENV NSUZUMIRA_MOCK=false

EXPOSE 8001
CMD ["python", "main.py"]
