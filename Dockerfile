# Use a smaller base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install Uvicorn
RUN pip install --no-cache-dir uvicorn

# Install dependencies separately to leverage caching
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY ./app /app

# Expose the default port
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
