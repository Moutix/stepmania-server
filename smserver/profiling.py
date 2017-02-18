""" Module to add profiling function to taemin """

import os
import tempfile
import cProfile
import pstats
import io
import time
from functools import wraps

from smserver import logger
from smserver import conf

LOGGER = logger.get_logger()


def get_profile_path(path):
    """ Get the path to use for profiling """

    if os.path.isdir(path):
        new_path = path
    else:
        new_path = os.path.dirname(path)

    if os.access(new_path, os.W_OK):
        return new_path

    new_path = tempfile.gettempdir()
    LOGGER.error("directory %r is not writable, using %r instead", path, new_path)
    return new_path


def profile(arg=None):
    """ Profile decorator:

        Add @profile.profile() on a function to profile it.
    """

    profile.path = None

    def profiling(func):
        """ Profiling inner decorator """


        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Wrapper function"""

            if not conf.config["profile_path"]:
                return func(*args, **kwargs)

            if not profile.path or profile.path != conf.config["profile_path"]:
                profile.path = get_profile_path(conf.config["profile_path"])

            profiling = cProfile.Profile()

            start = time.time()

            res = profiling.runcall(func, *args, **kwargs)

            # Execution time:
            delta = time.time() - start

            if arg in kwargs:
                name = "%s_%s" % (func.__name__, kwargs[arg].__class__.__name__)
            else:
                name = func.__name__

            stats_file = "%s/%f_%fs_%s" % (profile.path,
                                           time.time(),
                                           delta,
                                           name)

            LOGGER.info("Dumping stats to %r", stats_file)

            pstats.Stats(
                profiling,
                stream=io.StringIO()
            ).sort_stats("cumulative").dump_stats(stats_file)

            return res

        return wrapper
    return profiling
