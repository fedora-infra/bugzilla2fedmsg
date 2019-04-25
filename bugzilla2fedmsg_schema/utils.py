"""This contains utils to parse the message."""


def comma_join(fields, oxford=True):
    """ Join together words. """

    def fmt(field):
        return "'%s'" % field

    if not fields:
        # unfortunately this happens: we get 'modify' messages with no
        # 'changes', so we don't know what changed
        return "something unknown"
    elif len(fields) == 1:
        return fmt(fields[0])
    elif len(fields) == 2:
        return " and ".join([fmt(f) for f in fields])
    else:
        result = ", ".join([fmt(f) for f in fields[:-1]])
        if oxford:
            result += ","
        result += " and %s" % fmt(fields[-1])
        return result


def email_to_fas(email):
    """Try to get a FAS username from an email address. For now, this
    is a dumb version which just does the 'easy' part of what the full
    fat fedmsg_meta email2fas did - for fedoraproject.org addresses,
    we can just do this easily. For all other addresses, we really
    need that full feature added to fedora-messaging.
    """
    if email.endswith('@fedoraproject.org'):
        return (email.rsplit('@', 1)[0], True)
    return (email, False)
