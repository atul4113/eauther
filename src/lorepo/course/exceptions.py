# exceptions.py

class LessonAlreadyCreatedError(Exception):
    """Custom exception for when a lesson is already created."""
    pass

RETRY_ERRORS = (
    # Define which exceptions should be retried, e.g., TimeoutError or ConnectionError
    TimeoutError,
    ConnectionError,
)
