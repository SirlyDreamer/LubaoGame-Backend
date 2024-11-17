FROM python:3.11-slim
LABEL authors="Sirly"

COPY requirements.txt /tmp/requirements.txt

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

ENTRYPOINT ["python", "/app/server.py"]