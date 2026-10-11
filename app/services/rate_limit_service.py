
from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, status


login_attempts: dict[str, deque[float]] = defaultdict(deque)

RATE_LIMIT = 5
WINDOW_SECONDS = 60


def check_login_rate_limit(ip_address: str) -> None:
    current_time = time()
    attempts = login_attempts[ip_address]

    # Remove attempts older than 60 seconds
    while attempts and current_time - attempts[0] >= WINDOW_SECONDS:
        attempts.popleft()

    # Block requests after 5 attempts
    if len(attempts) >= RATE_LIMIT:
        retry_after = int(
            WINDOW_SECONDS - (current_time - attempts[0])
        ) + 1

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)}
        )

    attempts.append(current_time)
