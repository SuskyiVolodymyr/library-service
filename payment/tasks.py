from celery import shared_task


@shared_task
def checking_stripe_session():