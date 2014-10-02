import pyparsing as p

# Name part of a person
unquoted_name = p.Combine(p.OneOrMore(p.Word(''.join(set(p.printables) - {'<'}))))
quoted_name = p.Group('"' + unquoted_name + p.Suppress('"'))
name = p.Or([unquoted_name, quoted_name])

# Address itself
address_only = p.Word(p.printables)

# Combination of name and address
address = p.Or([
    name + p.Suppress('<') + address_only + p.Suppress('>'),
    address_only])

# Many addresses
addresses = p.OneOrMore(address)
