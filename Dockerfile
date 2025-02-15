FROM python:3.12-slim-bookworm

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Install Prettier globally
RUN npm install -g prettier@3.4.2

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure uv and Prettier are on the PATH
ENV PATH="/root/.local/bin/:/usr/local/bin/:$PATH"

# Set working directory
WORKDIR /app

# Copy the application file
COPY app.py /app

# Run the application using uv
CMD ["uv", "run", "app.py"]
