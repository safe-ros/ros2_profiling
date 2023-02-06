def filter_topics(collection, rosout: bool = False, parameter_events: bool = False):
    ret = []
    for val in collection:
        if not rosout and val.topic_name().find('rosout') >= 0:
            continue
        if not parameter_events and val.topic_name().find('parameter_events') >= 0:
            continue
        ret.append(val)
    return ret
