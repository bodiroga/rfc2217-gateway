#!/usr/bin/env python3

import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("serial2rfc2217 gateway program has started")