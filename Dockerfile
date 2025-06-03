FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies, Rust, and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && apt-get remove -y build-essential curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Poetry files first for dependency caching
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to not use virtualenvs (for Docker compatibility)
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code
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