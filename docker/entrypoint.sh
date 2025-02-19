#! /bin/bash

# Author: Abolfazl Kameli
# Version: v1.0.0
# Date: 2025-02-19
# Description: entrypoint for GSE API
# Usage: ./entrypoint.sh

python3 manage.py makemigrations --settings=core.settings.production
python3 manage.py migrate --settings=core.settings.production
python3 manage.py runserver --settings=core.settings.production 0.0.0.0:8000
