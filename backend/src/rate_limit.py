import time
import threading
from collections import deque
from typing import Callable, Dict

from fastapi import HTTPException, Request, status


_ALL_LIMITERS = []


class _SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._ip_to_hits: Dict[str, deque] = {}

    def check(self, ip: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            dq = self._ip_to_hits.setdefault(ip, deque())
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )
            dq.append(now)

    def reset(self) -> None:
        with self._lock:
            self._ip_to_hits.clear()


def make_ip_rate_limiter(max_requests: int, window_seconds: int = 60) -> Callable[[Request], None]:
    limiter = _SlidingWindowLimiter(max_requests=max_requests, window_seconds=window_seconds)
    _ALL_LIMITERS.append(limiter)

    def dependency(request: Request) -> None:
        # X-Forwarded-For first if present (when behind a proxy)
        xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
        if xff:
            ip = xff.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        limiter.check(ip)

    return dependency


def make_global_rate_limiter(max_requests: int, window_seconds: int = 60) -> Callable[[Request], None]:
    """Limit total requests across all IPs within a window.

    Useful against distributed bursts where per-IP limits are bypassed.
    """
    limiter = _SlidingWindowLimiter(max_requests=max_requests, window_seconds=window_seconds)
    _ALL_LIMITERS.append(limiter)

    def dependency(_: Request) -> None:
        limiter.check("__global__")

    return dependency


def reset_all_limiters() -> None:
    for lim in list(_ALL_LIMITERS):
        try:
            lim.reset()
        except Exception:
            pass


