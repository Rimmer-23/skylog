import os
from contextlib import contextmanager

import psycopg2


@contextmanager
def get_conn():
    # timezone=UTC: CURRENT_DATE and ::date in SQL are always evaluated in UTC
    conn = psycopg2.connect(os.environ['DATABASE_URL'], options='-c timezone=UTC')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
