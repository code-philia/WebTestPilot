FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 8000

# Start the Python server (which serves both API and static files)
CMD ["python3", "server.py"]