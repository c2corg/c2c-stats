#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# c2cstats - Compute statistics for camptocamp.org
# Copyright (C) 2009, 2010, 2011 - saimon.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see http://www.gnu.org/licenses/

"""
C2C user's stats
================

Compute some statistics for the outing list of a user.
"""

__author__ = "Simon <contact at saimon dot org>"
__version__ = "0.1"
__date__ = ""
__copyright__ = "Copyright (c) 2009, 2010 Simon <contact at saimon dot org>"
__license__ = "GPL"

# imports
import sys
import argparse
import os.path
from c2cstats.parser import C2CParser
from c2cstats.plots import C2CPlots
from c2cstats.settings import read_settings

def main():
    "main program"

    version = "version %s, %s" % (__version__, __date__)

    parser = argparse.ArgumentParser(description='Compute some statistics for camptocamp.org.')
    parser.add_argument('user_id', help='user id')
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version)
    args = parser.parse_args()

    settings = read_settings()
    settings['OUTPUT_DIR'] = os.path.join(settings['OUTPUT_DIR'],
                                          str(args.user_id))

    print ":: Compute stats for user %s ..." % args.user_id
    data = C2CParser(args.user_id)
    plots = C2CPlots(data, settings)
    plots.plot_all()
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
