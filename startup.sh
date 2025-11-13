#!/bin/bash

# Startup script for Azure App Service
gunicorn --bind=0.0.0.0 --timeout 600 app:app
