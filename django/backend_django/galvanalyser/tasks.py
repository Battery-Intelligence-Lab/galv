from celery import shared_task
from .models import Harvester
import os


@shared_task
def get_env():
    env_var = 'GALVANALYSER_HARVESTER_BASE_PATH'
    return {env_var: os.getenv(env_var)}


@shared_task
def run_harvester(harvester_id):
    Harvester.objects.get(id=harvester_id).run()
