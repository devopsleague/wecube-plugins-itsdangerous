# coding=utf-8
"""
wecube_plugins_itsdangerous.server.scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供定时清理能力

"""

from __future__ import absolute_import

import os
import shutil
import time
import datetime
import logging
from pytz import timezone
from talos.core import config
from talos.core import logging as mylogger

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from wecube_plugins_itsdangerous.server.wsgi_server import application

CONF = config.CONF
LOG = logging.getLogger(__name__)

jobstores = {'default': MemoryJobStore()}
executors = {'default': ThreadPoolExecutor(5)}
job_defaults = {'coalesce': False, 'max_instances': 1}


def cleanup_cached_dir():
    try:
        interval_min = 10
        try:
            interval_min = int(CONF.pakcage_cache_cleanup_interval_min)
        except Exception as e:
            LOG.error("Invalid package_cache_cleanup_interval_min: %s",
                      CONF.pakcage_cache_cleanup_interval_min)
        max_delta = interval_min * 60
        base_dir = CONF.pakcage_cache_dir
        if os.path.exists(base_dir):
            for name in list(os.listdir(base_dir)):
                fullpath = os.path.join(base_dir, name)
                path_stat = os.stat(fullpath)
                if time.time() - path_stat.st_atime > max_delta:
                    LOG.info('remove dir/file: %s, last access: %s', fullpath, path_stat.st_atime)
                    if os.path.isdir(fullpath):
                        shutil.rmtree(fullpath, ignore_errors=True)
                    elif os.path.isfile(fullpath):
                        os.remove(fullpath)
    except Exception as e:
        LOG.exception(e)


def rotate_log():
    try:
        logs = [CONF.log.gunicorn_access, CONF.log.gunicorn_error, CONF.log.path]
        extend_logs = getattr(CONF.log, 'loggers', [])
        for l in extend_logs:
            if l.get('path'):
                logs.append(l['path'])
        max_file_keep = 30
        for log_file in logs:
            results = []
            base_dir = os.path.dirname(log_file)
            if os.path.exists(base_dir):
                for name in list(os.listdir(base_dir)):
                    fullpath = os.path.join(base_dir, name)
                    if os.path.isfile(fullpath):
                        if fullpath.startswith(log_file + '.'):
                            timestamp = 0
                            try:
                                timestamp = int(fullpath.rsplit('.', 1)[1])
                                # ignore which not endswith datetime
                                results.append((timestamp, fullpath))
                            except Exception as e:
                                pass

            results.sort(key=lambda item: item[0])
            while len(results) >= max_file_keep:
                timestamp, fullpath = results.pop(0)
                try:
                    LOG.info('remove file: %s', fullpath)
                    os.remove(fullpath)
                except Exception as e:
                    LOG.info('remove file: %s error: %s', fullpath, str(e))
        for log_file in logs:
            new_log_file = log_file + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            if os.path.exists(log_file):
                try:
                    LOG.info('rename file: %s to %s', log_file, new_log_file)
                    os.rename(log_file, new_log_file)
                except Exception as e:
                    LOG.info('rename file: %s to %s error: %s', log_file, new_log_file, str(e))
    except Exception as e:
        LOG.exception(e)


def main():
    tz_info = timezone(CONF.timezone)
    try:
        if CONF.platform_timezone:
            tz_info = timezone(CONF.platform_timezone)
    except Exception as e:
        LOG.exception(e)
    scheduler = BlockingScheduler(jobstores=jobstores,
                                  executors=executors,
                                  job_defaults=job_defaults,
                                  timezone=tz_info)
    scheduler.add_job(cleanup_cached_dir, 'cron', minute="*/5")
    scheduler.add_job(rotate_log, 'cron', hour=3, minute=5)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()