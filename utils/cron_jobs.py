from apscheduler.schedulers.background import BackgroundScheduler
from authentication.models import BlackList


def start():
    """
    Initialize cron job.(Task that will be run everyday at 1am)
    This will call the function that deletes user tokens older
    than 24 hours
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        BlackList.delete_tokens_older_than_a_day,
        'cron', hour=1, minute=0
    )
    scheduler.start()
