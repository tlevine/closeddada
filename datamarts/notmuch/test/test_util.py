import re

import nose.tools as n

from ..util import (
    offlineimap_is_running, EMAIL_ADDRESS,
)

def test_EMAIL_ADDRESS():
    testcases = [
        ('Thomas Levine <no-reply@thomaslevine.com>', 'no-reply@thomaslevine.com'),
    ]
    for field, expected in testcases:
        yield check_EMAIL_ADDRESS, field, expected

def check_EMAIL_ADDRESS(field, expected):
    observed = re.match(EMAIL_ADDRESS, field)
    if expected == None:
        n.assert_equal(observed, expected)
    else:
        n.assert_not_equal(observed, None)
        n.assert_equal(observed.group(1), expected)
