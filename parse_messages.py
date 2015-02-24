import modules.time.check as time_check #import each module
import modules.time.get as time_get

import modules.test.check as test_check
import modules.test.get as test_get

def parse(message):
    if time_check.check(message["text"]):
        return time_get.get(message)
    elif test_check.check(message["text"]):
        return test_get.get(message)
    else:
        return None
