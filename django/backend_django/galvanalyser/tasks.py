from celery import shared_task
import os


@shared_task
def get_env():
    env_var = 'GALVANALYSER_HARVESTER_BASE_PATH'
    return {env_var: os.getenv(env_var)}
