import pyparsing as p

name = (p.Combine(p.OneOrMore(p.Word(p.printables))) |\
        p.QuotedString('"')).setResultsName('name')

address = (p.QuotedString('<', endQuoteChar = '>') |\
           p.Regex(r'[^<>" ]+@[^<>" ]+')).setResultsName('address')

pair = p.Group(name + address) | address

# Many addresses
addresses = p.delimitedList(pair)

def parse_addresses(raw):
    for pair in addresses.parseString(raw):
        if len(pair) == 2:
        yield name, address
