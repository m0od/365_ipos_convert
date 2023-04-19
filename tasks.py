from final import celery
import time


@celery.task(bind=True)
def add(self, a, b):
    time.sleep(5)
    self.update_state(state='XXXX',
                      meta={'status': 'askjchs'})
    time.sleep(5)
    return a + b