import nose.tools as n

from ..parse_addresses import addresses

TESTCASES = [
    ('Thomas Levine <road-bike@thomaslevine.com>',
        [('Thomas Levine', 'road-bike@thomaslevine.com')]),
]

def check(raw, parsed):
    n.assert_list_equal(list(addresses.parseString(raw)), parsed)

def test():
    for raw, parsed in TESTCASES:
        yield check, raw, parsed
