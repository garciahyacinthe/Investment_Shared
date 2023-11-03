
def partial_flat(obj, subobj):
    """
    Returns the initial object with subobj flatten within it
    :param obj: obj returned
    :param subobj: subobj to flat within
    """

    # subscriptable, ie dict-like object
    if hasattr(obj, '__getitem__'):
        for key, value in obj[subobj].items():
            obj[key] = value

    # non-subscriptable but subobj is subscriptable
    if not hasattr(obj, '__getitem__'):
        dico = {}
        # not very elegant, but info dict is nowhere to be found in obj.__dict__
        exec(f'dico.update(obj.{subobj})')
        for key, value in dico.items():
            obj.__dict__.update(dico)

    # TODO implement try except for list-like object or else
    return obj

def mapping_to_dict(app_object, mapping):
    """
    gathers infos from outsourced object to fit in a dict, according to a mapping
    :param app_object: object to map
    :param mapping: mapping dict
    """

    if not app_object:
        return {}

    if app_object is not None:
        # Subscriptable
        if hasattr(app_object, '__getitem__'):
            dico = {key: app_object[value] for key, value in mapping.items()}
        else:
            # make dict appears from built-in fct (doesn't return all attributes tho)
            app_object = app_object.__dict__
            dico = {key: app_object[value] for key, value in mapping.items()}
        return dico
    else:
        return {}
