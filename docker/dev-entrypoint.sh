#!/bin/bash

# Author: Abolfazl Kameli
# Version: v1.0.0
# Date: 2025-02-19
# Description: entrypoint for GSE API
# Usage: ./entrypoint.sh

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
