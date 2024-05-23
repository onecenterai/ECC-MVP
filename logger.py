import logging

log = logging.getLogger(__name__)

info_handler = logging.FileHandler('/sw_log.log')
info_handler.setLevel(logging.INFO)

# info_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# info_handler.setFormatter(info_format)

log.addHandler(info_handler)