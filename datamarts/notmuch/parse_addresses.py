import pyparsing as p

# Name part of a person
chars = ''.join(set(p.printables) - set('"<>'))
unquoted_name = p.Combine(p.OneOrMore(p.Word(chars)))
quoted_name = p.Suppress('"') + unquoted_name + p.Suppress('"')
name = p.Or([unquoted_name, quoted_name])

# Address itself
address_only = p.Word(chars)

# Combination of name and address
address = p.Or([
    address_only,
    name + p.Suppress(p.Optional('<')) + address_only + p.Suppress('>')
])

# Many addresses
addresses = p.OneOrMore(p.Group(address))

def parse_addresses(raw):
    for parsed in addresses.parseString(raw):
        name = ' '.join(parsed[:-1])
        address = parsed[-1]
        yield name, address
