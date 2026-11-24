"""SQLite result cache so re-running an unchanged suite makes zero model calls."""
import os, sqlite3, hashlib, json, threading
_lock = threading.Lock()
_c = sqlite3.connect(os.getenv('LLMEVAL_CACHE', '.llmeval_cache.db'), check_same_thread=False)
_c.execute('CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT)')

def key(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()

def cached(k: str, fn, enabled: bool = True):
    if enabled:
        with _lock:
            row = _c.execute('SELECT v FROM cache WHERE k=?', (k,)).fetchone()
        if row: return json.loads(row[0])
    v = fn()
    with _lock:
        _c.execute('INSERT OR REPLACE INTO cache VALUES (?,?)', (k, json.dumps(v))); _c.commit()
    return v

def clear() -> None:
    with _lock:
        _c.execute('DELETE FROM cache'); _c.commit()
