"""
Shared backend utilities: Mongo doc serialization + simple in-memory rate limiting.
"""
from datetime import datetime
from collections import defaultdict
import time
from fastapi import HTTPException


def serialize_doc(doc: dict) -> dict:
    """Strip Mongo _id and convert datetime objects to ISO strings."""
    if not doc:
        return doc
    doc = dict(doc)
    doc.pop('_id', None)
    for k, v in list(doc.items()):
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


_rate_buckets = defaultdict(list)


def check_rate_limit(key: str, max_requests: int = 20, window_seconds: int = 60):
    """Simple sliding-window in-memory rate limiter. Raises 429 if exceeded."""
    now = time.time()
    bucket = _rate_buckets[key]
    while bucket and bucket[0] < now - window_seconds:
        bucket.pop(0)
    if len(bucket) >= max_requests:
        raise HTTPException(status_code=429, detail='Rate limit exceeded. Please slow down and try again shortly.')
    bucket.append(now)
