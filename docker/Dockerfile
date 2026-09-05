FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libgeos-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-full.txt .

RUN pip install --no-cache-dir -r requirements-full.txt

COPY backend/app ./app
COPY backend/models ./models
COPY backend/outputs ./outputs
COPY RoadGIE ./RoadGIE

RUN mkdir -p \
    outputs/visualizations \
    uploads/atlas \
    outputs/reports \
    generated
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]