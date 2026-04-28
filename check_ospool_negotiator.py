#!/usr/bin/env python3

import optparse
import sys
import time
import htcondor2

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
    print(str(high_level) + " \"" + pool + " Negotiator\" - " + desc)
    sys.exit(high_level)


def check(pool):
    """
    Query the HTCondor negotiator classad via the collector and verify:
      - LastNegotiationCycleEnd0 is within the last 10 minutes
      - LastNegotiationCycleDuration0 < 120
      - LastNegotiationCycleCandidateSlots0 > 10000
    """

    negotiator_ad = None
    source_cm = None

    constraint = ' || '.join(
        'Name == "cm-%d.%s.osg-htc.org"' % (i, pool) for i in [1, 2]
    )

    for cm in ["cm-1", "cm-2"]:
        try:
            coll = htcondor2.Collector("%s.%s.osg-htc.org" % (cm, pool))
            ads = coll.query(
                htcondor2.AdTypes.Negotiator,
                constraint=constraint,
                projection=[
                    "Name",
                    "LastNegotiationCycleEnd0",
                    "LastNegotiationCycleDuration0",
                    "LastNegotiationCycleCandidateSlots0",
                ]
            )
            if ads:
                negotiator_ad = ads[0]
                source_cm = cm
                break
        except Exception as e:
            reg_issue(WARN, "Unable to query negotiator via %s: %s" % (cm, e))

    if negotiator_ad is None:
        reg_issue(CRITICAL, "No negotiator classad found")
        report(pool)

    now = int(time.time())

    # LastNegotiationCycleEnd0: must be within the last 10 minutes
    cycle_end = negotiator_ad.get("LastNegotiationCycleEnd0")
    if cycle_end is None:
        reg_issue(CRITICAL, "LastNegotiationCycleEnd0 missing from negotiator ad")
    else:
        age = now - int(cycle_end)
        if age > 600:
            reg_issue(CRITICAL, "Last negotiation cycle ended %ds ago (>10min)" % age)
        else:
            reg_issue(OK, "Last cycle ended %ds ago" % age)

    # LastNegotiationCycleDuration0: must be < 120 seconds
    duration = negotiator_ad.get("LastNegotiationCycleDuration0")
    if duration is None:
        reg_issue(CRITICAL, "LastNegotiationCycleDuration0 missing from negotiator ad")
    else:
        duration = int(duration)
        if duration >= 120:
            reg_issue(CRITICAL, "Negotiation cycle duration %ds (>=120s)" % duration)
        else:
            reg_issue(OK, "Cycle duration %ds" % duration)

    # LastNegotiationCycleCandidateSlots0: must be > 10000
    slots = negotiator_ad.get("LastNegotiationCycleCandidateSlots0")
    if slots is None:
        reg_issue(CRITICAL, "LastNegotiationCycleCandidateSlots0 missing from negotiator ad")
    else:
        slots = int(slots)
        if slots <= 10000:
            reg_issue(CRITICAL, "Candidate slots %d (<=10000)" % slots)
        else:
            reg_issue(OK, "Candidate slots %d" % slots)

    report(pool)


# Configure command line option parser
parser = optparse.OptionParser()
parser.add_option("--pool", dest="pool", choices=["ospool", "ospool-itb"],
                  help="Pool to check: ospool or ospool-itb")
(options, args) = parser.parse_args()

if not options.pool:
    options.pool = "ospool"

check(options.pool)
