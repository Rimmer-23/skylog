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
            transform(bronze_id)
            log.info(f'{name}: bronze id={bronze_id}, silver done')
        except Exception as e:
            log.error(f'{name}: failed: {e}', exc_info=True)
            failed.append(name)

    try:
        aggregate()
        log.info('Gold: aggregates updated')
    except Exception as e:
        log.error(f'Gold failed: {e}', exc_info=True)
        failed.append('gold')

    if failed:
        raise RuntimeError(f'Pipeline finished with errors: {", ".join(failed)}')
    log.info('=== Pipeline done ===')
