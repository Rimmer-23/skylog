import logging

from aggregate import aggregate
from extract import extract
from transform import transform

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        log.info('=== Pipeline start ===')
        bronze_id = extract()
        log.info(f'Bronze: saved raw data, id={bronze_id}')
        transform(bronze_id)
        log.info('Silver: transform done')
        aggregate()
        log.info('Gold: aggregates updated')
        log.info('=== Pipeline done ===')
    except Exception as e:
        log.error(f'Pipeline failed: {e}', exc_info=True)
        raise
