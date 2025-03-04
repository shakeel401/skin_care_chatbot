# Use an official Python base image
FROM python:3.10

# Set environment variables to prevent .pyc files and enable buffering
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies separately to leverage Docker caching
COPY requirements.txt .

# Remove pywin32 from requirements.txt to avoid Linux installation issues
RUN sed -i '/pywin32/d' requirements.txt && pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose the port that your FastAPI app listens on
EXPOSE 80

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
