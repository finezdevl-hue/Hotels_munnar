#!/bin/bash

echo "==== Install requirements ===="
pip install -r requirements.txt

echo "==== Run migrations ===="
python manage.py migrate

echo "==== Collect static ===="
python manage.py collectstatic --noinput

echo "==== Create superuser ===="
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@gmail.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created")
else:
    print("Superuser already exists")
EOF

echo "==== Build finished ===="