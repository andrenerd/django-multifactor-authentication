# RESERVED # from __future__ import absolute_import # for Celery

# RESERVED
# try:
#     from .celery import app as celery_app
#     celery = True
# except ImportError:
#     celery = False
celery = False


class AbstractProvider:
    """
    Low level communication-specific providers for 
    different type of "devices" (check the devices folder)
    """

    def __init__(self, to, *args, **kwargs):
        self.to = to

    # RESERVED
    # def send(self):
    #     if celery:
    #         send_task.delay(self)
    #     else:
    #         self._send()

    def send(self):
        self._send()

    def _send(self):
        if not self.to:
            return

        raise NotImplementedError



# RESERVED
# @shared_task # loaddata doesn't handle it :(
# @celery_app.task
# def send_task(mail):
#     """
#     Called asynchronosly via Celery
#     """
#     mail._send()
