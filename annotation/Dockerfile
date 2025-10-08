FROM python:3.11-slim

WORKDIR /app

# Copy all files to the container
COPY . .

# Expose port 3000
EXPOSE 3000

# Start the Python server (which serves both API and static files)
CMD ["python3", "server.py"]