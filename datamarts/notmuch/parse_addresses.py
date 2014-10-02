import pyparsing as p

unquoted_name = p.Combine(p.OneOrMore(p.Word(exclude_chars = '<')))
quoted_name = p.Group('"' + unquoted_name + p.Suppress('"'))
name = p.Or([unquoted_name, quoted_name])
addresses = p.OneOrMore(p.Or([
    name + p.Suppress('<') + p.Word(p.printables) + p.Suppress('>'),
    p.Word(printables)]))
