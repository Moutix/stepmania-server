""" Start up module.

Use this module to setup the stepmania environment
"""

from smserver import logger

def start_up(config):
    """ Initalize all the stepmania environment """

    logger.set_logger_options(config.logger)
