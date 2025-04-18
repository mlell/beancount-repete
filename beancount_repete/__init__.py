import copy, datetime
from dateutil import rrule
from recurrent import parse
from recurrent.event_parser import RecurringEvent
from beancount.core import data

__plugins__ = [ 'repete', ]

REPETE = 'repete'


def parse_config(str):
    config = {
        "repeat_limit" : "in one year"
    }
    if not config: return config
    str = str.split(",")
    str = [ x.split("=", 1) for x in str ]
    for k, v in str:
        if k not in config:
            raise ValueError(f"Unknown option {k}, use one of {",".join(config.keys())}")
        config[k] = v

    # need to give a single point in time (not a recurring event or a string the
    # library can't parse)
    config["repeat_limit"] = parse(config["repeat_limit"])
    if not isinstance(config["repeat_limit"], datetime.datetime):
        raise ValueError(f"Not a point in time: {repeat_limit}")

    return config



def repete(entries, options, config):

    config = parse_config(config)
    repeat_limit = config["repeat_limit"]

    new_entries = []
    rubbish_bin = []
    for txn in data.filter_txns(entries):
        if REPETE in txn.meta:
            rubbish_bin.append(txn)
            re = RecurringEvent(now_date=txn.date)
            re.parse(txn.meta[REPETE])
            for i in rrule.rrulestr(re.get_RFC_rrule(), dtstart=txn.date):
                if i > repeat_limit: break
                new = copy.deepcopy(txn)
                new = new._replace(date=i.date())
                del new.meta[REPETE]
                new_entries.append(new)

    for txn in rubbish_bin:
        entries.remove(txn)

    return entries + new_entries, []
