import functools
import logging
import time
import urllib.parse

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import TransientError as Neo4jTransientError
from neomodel import config as neomodel_config
from neomodel import db

from common.exceptions import BusinessLogicException

log = logging.getLogger(__name__)

# Teach urljoin that Neo4j DSN URLs like bolt:// and neo4j:// semantically similar to http://
for scheme in ("bolt", "bolt+s", "neo4j", "neo4j+s"):
    urllib.parse.uses_relative.append(scheme)
    urllib.parse.uses_netloc.append(scheme)


def is_transient_lock_error(exc: Exception) -> bool:
    """
    Returns True if exception is a transient database lock conflict or deadlock error.
    Does NOT match permanent database connection failures or schema errors.
    """
    if isinstance(exc, Neo4jTransientError):
        return True
    exc_name = exc.__class__.__name__
    if any(k in exc_name for k in ("TransientError", "LockClientStopped", "Deadlock")):
        return True
    msg = str(exc)
    if any(k in msg for k in ("TransientError", "LockClientStopped", "Unable to acquire lock", "Deadlock")):
        return True
    return False


def retry_on_transient_lock(
    max_retries: int = 5,
    initial_delay: float = 0.05,
    backoff_factor: float = 2.0,
    max_delay: float = 0.5,
    max_total_delay: float = 2.0,
):
    """
    Decorator for retrying database transactions on transient lock contention.
    Only retries if called as the outermost transaction boundary (i.e. when no
    transaction was active before entering).
    Guarantees max total backoff delay <= max_total_delay (default 2.0s).
    Re-executes the wrapped transaction function on failure.
    If retries exhaust, raises BusinessLogicException.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            in_existing_tx = getattr(db, "_active_transaction", None) is not None
            if in_existing_tx:
                return func(*args, **kwargs)

            delay = initial_delay
            total_delay = 0.0
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    attempt += 1
                    if not is_transient_lock_error(exc):
                        raise

                    if attempt > max_retries or total_delay >= max_total_delay:
                        log.warning(
                            "Transaction retries exhausted after %d attempts and %.2fs total delay for %s: %s",
                            attempt, total_delay, getattr(func, "__qualname__", str(func)), exc
                        )
                        raise BusinessLogicException(
                            msg="The operation could not be completed due to concurrent database locks. Please try again."
                        ) from exc

                    sleep_time = min(delay, max_delay, max_total_delay - total_delay)
                    if sleep_time <= 0:
                        raise BusinessLogicException(
                            msg="The operation could not be completed due to concurrent database locks. Please try again."
                        ) from exc

                    log.info(
                        "Transient lock conflict in %s (attempt %d/%d). Retrying in %.3fs...",
                        getattr(func, "__qualname__", str(func)), attempt, max_retries, sleep_time
                    )
                    time.sleep(sleep_time)
                    total_delay += sleep_time
                    delay *= backoff_factor
        return wrapper
    return decorator


def configure_database(
    neo4j_dsn: str, /, soft_cardinality_check: bool = True, **driver_options
) -> Driver:
    parsed = urllib.parse.urlparse(neo4j_dsn)

    if parsed.scheme not in (
        "bolt",
        "neo4j",
        "bolt+s",
        "neo4j+s",
        "bolt+ssc",
        "neo4j+ssc",
    ):
        raise ValueError(f"Unsupported scheme in NEO4J_DSN: {parsed.scheme}")

    database_name = parsed.path.lstrip("/") or "neo4j"
    username = parsed.username or "neo4j"
    password = parsed.password or ""

    driver = GraphDatabase.driver(
        database_uri(neo4j_dsn),
        auth=(username, password),
        database=database_name,
        **driver_options,
    )

    neomodel_config.DRIVER = driver
    neomodel_config.DATABASE_NAME = database_name
    neomodel_config.DATABASE_URL = None
    neomodel_config.SOFT_CARDINALITY_CHECK = soft_cardinality_check

    return driver


def database_uri(dsn: str) -> str:
    parsed = urllib.parse.urlparse(dsn)
    return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
