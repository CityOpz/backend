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

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system appgroup && \
  useradd --system --gid appgroup --home-dir /app appuser

COPY --chown=appuser:appgroup manage.py /app/manage.py
COPY --chown=appuser:appgroup cityops /app/cityops
COPY --chown=appuser:appgroup apps /app/apps
COPY --chown=appuser:appgroup wait-for-it.sh /app/wait-for-it.sh
COPY --chown=appuser:appgroup start.sh /app/start.sh
COPY --chown=appuser:appgroup pytest.ini /app/pytest.ini

RUN chmod +x /app/wait-for-it.sh /app/start.sh

USER appuser
