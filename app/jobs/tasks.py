#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import datetime

from celery.utils.log import get_task_logger

from app.jobs.celery_app import celery_app
from application import app
from app.dao.fastdfs import FastDFSStorage

storage = FastDFSStorage()

app.app_context().push()
logger = get_task_logger(__name__)


@celery_app.task()
def check_declaration():
    ...