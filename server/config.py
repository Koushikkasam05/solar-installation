# -*- coding: utf-8 -*-
"""SolarFlow ERP - Configuration & Environment Constants."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_APP_DIR = os.path.join(BASE_DIR, 'web_app')
if not os.path.exists(WEB_APP_DIR):
    WEB_APP_DIR = os.path.join(BASE_DIR, 'solar-installation-main', 'web_app')

SECRET_KEY = 'solarflow_secret_key_2026'
DATABASE = os.path.join(BASE_DIR, 'solarflow.db')
