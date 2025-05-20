FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app

# Install system dependencies and Rust
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . $HOME/.cargo/env \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install -U psutil \
    && pip install -U aiohttp==3.9.0rc0 \
    # Cleanup to reduce image size
    && apt-get remove -y build-essential curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app

# Set permissions
RUN chmod -R 755 /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Expose port
EXPOSE 5001

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
