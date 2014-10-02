import nose.tools as n

from ..parse_addresses import parse_addresses

TESTCASES = [
    ('Thomas Levine <road-bike@thomaslevine.com>',
        [('Thomas Levine', 'road-bike@thomaslevine.com')]),
    ('"Thomas Levine" <road-bike@thomaslevine.com>',
        [('Thomas Levine', 'road-bike@thomaslevine.com')]),
    ('public@thomaslevine.com',
        [(None, 'public@thomaslevine.com')]),
]

def check(raw, parsed):
    n.assert_list_equal(list(parse_addresses(raw)), parsed)

def test():
    for raw, parsed in TESTCASES:
        yield check, raw, parsed
