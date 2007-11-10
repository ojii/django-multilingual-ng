def to_str(arg):
    """
    Convert all unicode strings in a structure into 'str' strings.

    Utility function to make it easier to write tests for both
    unicode and non-unicode Django.
    """
    if type(arg) == list:
        return [to_str(el) for el in arg]
    elif type(arg) == tuple:
        return tuple([to_str(el) for el in arg])
    elif arg is None:
        return None
    else:
        return str(arg)
