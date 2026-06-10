FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY Life_Prescriber/ .

# Collect static files using a build-only placeholder key
RUN DJANGO_SECRET_KEY=build-placeholder \
    DEBUG=False \
    ALLOWED_HOSTS=* \
    python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "Life_Prescriber.wsgi:application", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--timeout", "120"]
