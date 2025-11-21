#!/usr/bin/env python3

import optparse
import sys
import time
import os
import re
import glob
import htcondor2
import classad2

UNKNOWN  = 3
CRITICAL = 2
WARN     = 1
OK       = 0

issues = []


def reg_issue(level, msg):
    issues.append([level, msg])

def report(pool):

    desc = ""
    high_level = 0
    for level in [UNKNOWN, CRITICAL, WARN, OK]:
        for issue in issues:
            if issue[0] == level:
                if desc != "":
                    desc += ",  "
                desc += issue[1]
                if level > high_level:
                    high_level = level
    print(str(high_level) + " \"OSG " + pool + "\" - " + desc)
    sys.exit(high_level)


def check(pool):
    """
    The tests to perform in the given order. Check at logically places
    if we should short-circuit the testing.
    """

    succeeded = 0
    failed = 0

    # CCBs
    for ccb in ["ccb-1", "ccb-2"]:
        try:
            coll = htcondor2.Collector("%s.%s.osg-htc.org"%(ccb, pool))
            ads = coll.query(projection=["Name"])
            if len(ads) < 5:
                reg_issue(WARN, "Missing daemons on %s"%(ccb))
            else:
                succeeded += 1
        except Exception as e:    
            reg_issue(CRITICAL, "Unable to connect to %s"%(ccb))
            failed += 1
    
    # CMs
    ads = {}
    for cm in ["cm-1", "cm-2"]:
        ads[cm] = []
        try:
            coll = htcondor2.Collector("%s.%s.osg-htc.org"%(cm, pool))
            ads[cm] = coll.query(projection=["Name"])
            succeeded += 1
        except:
            reg_issue(CRITICAL, "Unable to connect to %s"%(cm))
            failed += 1

    if len(ads["cm-1"]) > 0 and len(ads["cm-2"]) > 0:
        diff = abs(len(ads["cm-1"]) - len(ads["cm-2"]))
        percent_diff = int(diff / len(ads["cm-1"]) * 100)
        percent_diff = min(percent_diff, 100) 
        if percent_diff > 20:
            reg_issue(WARN, "%d%% difference in ads between cm-1 and cm-2"%(percent_diff))
            failed += 1
        # always show ad count
        reg_issue(OK, "Ads at collectors: cm-1=%d, cm-2=%d"%(len(ads["cm-1"]), len(ads["cm-2"])))
  
    # Reporting time. If at least _one_ of the checked files
    # succeeded, report success!
    if succeeded > 0 and failed == 0:
        report(pool)

    # failures
    if succeeded == 0:
        reg_issue(WARN, "No checks succeeded")
        report(pool)
    if failed > 0:
        #reg_issue(WARN, "%d checks failed" %(failed))
        report(pool)

    reg_issue(WARN, "Unknown error")
    report(pool)

# Configure command line option parser
parser = optparse.OptionParser()
parser.add_option("--pool", dest="pool", choices=["ospool", "ospool-itb"], 
                  help="Pool to check: ospool or ospool-itb")
(options, args) = parser.parse_args()

if not options.pool:
    options.pool = "ospool"

check(options.pool)

