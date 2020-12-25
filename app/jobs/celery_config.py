#!/usr/bin/python
# -*- coding:utf-8 -*-

from app.configs import CONFIG
from celery.schedules import crontab


BROKER_URL = CONFIG.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = CONFIG.CELERY_BACKEND_URL

CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

CELERYBEAT_SCHEDULE = {
    'ch_declaration': {
        'task': 'app.jobs.tasks.check_declaration',
        'schedule': crontab(0, 0, day_of_month='1')
    }
}
