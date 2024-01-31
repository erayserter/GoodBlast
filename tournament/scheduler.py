import os

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from tournament.models import Tournament


def tournament_scheduler_job():
    Tournament.create_daily_tournament()


def start():
    if os.environ.get('RUN_MAIN') != 'true':
        return

    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    days_to_store = 7
    days_in_seconds = days_to_store * 24 * 60 * 60

    DjangoJobExecution.objects.delete_old_job_executions(days_in_seconds)

    scheduler.add_job(
        tournament_scheduler_job,
        trigger=CronTrigger(hour=12, minute=0, timezone=pytz.utc),
        id="tournament_scheduler_job",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()
