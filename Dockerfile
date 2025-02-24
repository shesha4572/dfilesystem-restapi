FROM python:3.12-slim
LABEL authors="shesha4572"

WORKDIR /app
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
COPY . .

EXPOSE 6800
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6800"]
