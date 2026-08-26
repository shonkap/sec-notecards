FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Tkinter GUI dependencies for this app.
# Some upstream images include a stale Yarn apt source that can break apt-get update.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
   && rm -f /etc/apt/sources.list.d/yarn.list.save

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-tk \
       libx11-6 \
       libxext6 \
       libxrender1 \
       libxtst6 \
       libxi6 \
    && rm -rf /var/lib/apt/lists/*