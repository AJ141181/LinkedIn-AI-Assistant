# Use official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy entire project contents into the container
COPY . /app

# Explicitly copy credentials (required for Google APIs)
COPY secrets/credentials.json backend/keys/credentials.json

# Ensure backend is recognized as a module
RUN touch backend/__init__.py

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variable for Google credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=backend/keys/credentials.json

# Expose port for Cloud Run
EXPOSE 8080

# Start the Flask app
CMD ["python", "-m", "backend.main"]
