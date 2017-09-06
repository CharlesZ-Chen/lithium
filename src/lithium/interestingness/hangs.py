#!/usr/bin/env python
# coding=utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Lithium's "hangs" interestingness test to assess whether a binary hangs.

Example:
    python -m lithium hangs 3 ./js --fuzzing-safe testcase.js
"""

from __future__ import absolute_import

import logging

from . import timed_run


def interesting(cli_args, temp_prefix):
    """Interesting if the binary causes a hang.

    Args:
        cli_args (list): List of input arguments.
        temp_prefix (str): Temporary directory prefix, e.g. tmp1/1 or tmp4/1

    Returns:
        bool: True if binary causes a hang, False otherwise.
    """
    logger = logging.getLogger("interestingness_hangs")
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("flake8").setLevel(logging.WARNING)
    logger_handler = logging.StreamHandler()

    timeout = int(cli_args[0])
    runinfo = timed_run.timed_run(cli_args[1:], timeout, temp_prefix)

    if runinfo.sta == timed_run.TIMED_OUT:
        return True

    logger.info("Exited in %.3f seconds", runinfo.elapsedtime)
    logger_handler.flush()
    return False
