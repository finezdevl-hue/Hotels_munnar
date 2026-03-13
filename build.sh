#!/bin/bash

echo "Install requirements"
pip install -r requirements.txt

echo "Run migrate"
python manage.py migrate --noinput

echo "Collect static"
python manage.py collectstatic --noinput --clear

echo "Done"