web: gunicorn tutorial.wsgi:application
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput

