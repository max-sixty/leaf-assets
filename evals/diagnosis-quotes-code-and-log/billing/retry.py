import functools
import logging
import time

log = logging.getLogger("retry")


def retry(attempts, backoff_seconds, on):
    """Call the function again, up to `attempts` times in all, when it raises one of `on`."""

    def wrap(fn):
        @functools.wraps(fn)
        def call(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on as error:
                    if attempt == attempts:
                        raise
                    log.warning(
                        "%s failed (attempt %d of %d): %s; retrying in %ds",
                        fn.__name__, attempt, attempts, error, backoff_seconds,
                    )
                    time.sleep(backoff_seconds)

        return call

    return wrap
