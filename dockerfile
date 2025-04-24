# FROM python:3.12.9-slim
FROM python:3.12.9-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

# RUN apt-get update && apt-get install -y curl

# RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# RUN useradd -m -r osmar

# USER osmar

RUN mkdir -p /app/logs

COPY . /app

WORKDIR /app

# RUN pip install --upgrade pip

RUN pip install uv

# RUN exec $HOME/.local/bin/uv sync

RUN uv sync

VOLUME /app/logs/

CMD ["uv", "run", "main.py"]

