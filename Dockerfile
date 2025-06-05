# Use a smaller base image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Install Uvicorn
RUN pip install --no-cache-dir uvicorn

# Copy requirements first to leverage caching
COPY ./app/requirements.txt requirements.txt

# Install packages one by one with verbose output
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app .

# Expose the default port
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
