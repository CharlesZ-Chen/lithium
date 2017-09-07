#!/usr/bin/env python
# coding=utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Repeats an interestingness test a given number of times. If "RANGENUM" is present, it is replaced in turn with each
number in the range. This "RANGENUM" can be customized if required.

Use for:

1. Intermittent testcases.

   Repeating the test can make the bug occur often enough for Lithium to make progress.

    python -m lithium range 1 20 crashes --timeout=9 ./js --fuzzing-safe testcase.js

2. Unstable testcases.

   Varying a number in the test (using RANGENUM) may allow other parts of the testcase to be
   removed (Lithium), or may allow different versions of the shell to crash (autoBisect).

   In the testcase:
     schedulegc(n);

   On the command line:
     python -m lithium range 1 20 crashes --timeout=9 ./js --fuzzing-safe -e "n=RANGENUM;" testcase.js
"""

from __future__ import absolute_import

import argparse
import logging

from .utils import rel_or_abs_import


def interesting(cli_args, temp_prefix):
    """Interesting if the desired interestingness test that is run together with "range" also reports "interesting".

    Args:
        cli_args (list): List of input arguments.
        temp_prefix (str): Temporary directory prefix, e.g. tmp1/1 or tmp4/1

    Returns:
        bool: True if the desired interestingness test also returns True, False otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--rangenum", default="RANGENUM", dest="range_num",
                        help="Set the cookie that is to be altered in the testcase. Defaults to '%(default)s'.")
    parser.add_argument("cmd_with_flags", nargs=argparse.REMAINDER)
    args = parser.parse_args(cli_args)

    logger = logging.getLogger("interestingness_range")
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("flake8").setLevel(logging.WARNING)
    logger_handler = logging.StreamHandler()
    # logger_handler.terminator = ""  # We cannot yet suppress the ending newline yet, until Python 2.7 is deprecated

    loop_min = int(args.cmd_with_flags[0])
    loop_max = int(args.cmd_with_flags[1])
    assert loop_min >= 1, "Mininum number of iterations should be at least 1"
    assert (loop_max - loop_min) >= 0

    condition_script = rel_or_abs_import(args.cmd_with_flags[2])
    condition_args = args.cmd_with_flags[3:]

    if hasattr(condition_script, "init"):
        condition_script.init(condition_args)

    # Run the program over as many iterations as intended, with desired flags, replacing RANGENUM where necessary.
    for i in range(loop_min, loop_max + 1):
        # This doesn't do anything if RANGENUM is not found.
        replaced_condition_args = [s.replace("RANGENUM", str(i)) for s in condition_args]
        logger.info("Range number %d:", i)
        logger_handler.flush()
        if condition_script.interesting(replaced_condition_args, temp_prefix):
            return True

    return False
