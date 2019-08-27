release: python manage.py makemigrations authentication property transactions
release: python manage.py migrate

web: gunicorn landville.wsgi
worker: celery -A landville worker -l info
