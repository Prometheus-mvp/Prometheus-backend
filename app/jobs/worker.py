"""RQ worker bootstrap and runner."""
import logging

from redis import from_url
from rq import Connection, Queue, Worker

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_redis_connection():
    """Create Redis connection from settings."""
    return from_url(settings.redis_url)


def run_worker(queues: list[str] | None = None) -> None:
    """Run an RQ worker."""
    queues = queues or ["default"]
    redis_conn = get_redis_connection()
    with Connection(redis_conn):
        worker = Worker(map(Queue, queues))
        logger.info("Starting RQ worker", extra={"queues": queues})
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    run_worker()

