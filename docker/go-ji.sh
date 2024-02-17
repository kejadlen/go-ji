#!/bin/sh

alembic upgrade head
gunicorn --bind 0.0.0.0:8000 --capture-output --error-logfile - "go_ji:create_app()"
