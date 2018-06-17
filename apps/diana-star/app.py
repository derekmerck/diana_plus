# Start a diana-star worker:
#
# $ export DIANA_BROKER=redis://redis_host/1
# $ export DIANA_RESULT=redis://redis_host/2
# $ celery apps/diana-star/app.py worker -N diana_worker

from diana.star import app

if __name__ == '__main__':
    app.start()
