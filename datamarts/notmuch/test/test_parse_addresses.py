from ..parse_addresses import addresses

TESTCASES = [
    ('Thomas Levine <road-bike@thomaslevine.com>',
        [('Thomas Levine', 'road-bike@thomaslevine.com')]),
]

def check(raw, parsed):
    n.assert_equal(addresses.parseString(raw), parsed)

def test():
    for raw, parsed in testcases:
        yield check, raw, parsed
