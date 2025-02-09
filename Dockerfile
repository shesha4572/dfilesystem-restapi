FROM python:3.12-slim
LABEL authors="shesha4572"

WORKDIR /app
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
COPY . .
ENV DFS_MASTER_NODE_URL="http://cdn-master-0.cdn-master:8001"
ENV DFS_SLAVE_SERVICE_URL="cdn-slaves:9001"
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
