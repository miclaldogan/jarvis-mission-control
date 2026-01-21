# Placeholder Dockerfile for backend
# Will be implemented once backend framework is chosen

FROM python:3.11-slim

WORKDIR /app

# Keep image buildable even before deps exist
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . .

CMD ["python", "-c", "print('backend scaffold')"]
