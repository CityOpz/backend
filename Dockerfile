FROM python:3.12.4-slim-bullseye

# Install necessary tools to compile and install GDAL
RUN apt-get update && \
  apt-get install -y \
  binutils \
  libproj-dev \
  gdal-bin \
  libgdal-dev \
  python3-gdal \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt \
  && groupadd --system appgroup && \
  useradd --system --gid appgroup --home-dir /app appuser

COPY manage.py /app/manage.py
COPY cityops /app/cityops
COPY apps /app/apps
COPY wait-for-it.sh /app/wait-for-it.sh
COPY start.sh /app/start.sh
COPY pytest.ini /app/pytest.ini

RUN chmod 755 /app/wait-for-it.sh /app/start.sh && \
  chmod -R go-w /app

USER appuser
