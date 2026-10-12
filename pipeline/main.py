import logging

from aggregate import aggregate
from extract import extract
from locations import LOCATIONS
from transform import transform

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

if __name__ == '__main__':
    log.info('=== Pipeline start ===')
    failed = []
    # A failure in one city must not stop the others
    for name, lat, lon in LOCATIONS:
        try:
            bronze_id = extract(name, lat, lon)
            hours = transform(bronze_id)
            log.info('%s: bronze id=%s, silver rows=%s', name, bronze_id, hours)
        except Exception:
            log.exception('%s: failed', name)
            failed.append(name)

    try:
        aggregate()
        log.info('Gold: aggregates updated')
    except Exception:
        log.exception('Gold failed')
        failed.append('gold')

    if failed:
        raise RuntimeError(f'Pipeline finished with errors: {", ".join(failed)}')
    log.info('=== Pipeline done ===')
