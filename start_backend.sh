#!/bin/bash
exec /home/ubuntu/ph-callcenter-slm-app/venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
