#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
utils
"""


def dict_path_get(dictionary, path, defaultValue=None):
    """
    gets a value from the config data.
    can also take a path using the period as a separator.
    eg "first.second.third"
    """

    if not path:
        return None

    parts = path.split(".")
    num_parts = len(parts)
    cur_dict = dictionary

    try:
        # print "dict_path_get:", path
        for i in range(0, num_parts):
            part = parts[i]
            if part.isdigit():
                part = int(part)
            if isinstance(cur_dict, basestring):
                return defaultValue
            # print "\t> (", cur_dict, ":", part, ")"
            cur_dict = cur_dict[part]

        """
        if path not in ["data.id", "data.parent_id"]:
            print "path:", path
            print "num_parts: ", num_parts, type(num_parts)
            print "parts: ", parts[num_parts-1], type(parts[num_parts-1])
            print "cur_dict: ", cur_dict, type(cur_dict)
            print "\n"
        """
        
        return cur_dict
        #return cur_dict[parts[num_parts-1]]
    except (KeyError, IndexError):
        return defaultValue



class DictAccessor(object):
    """
    """

    def __init__(self, dictionary):
        """
        Constructor
        """

        self.dict = dictionary

    def get(self, path, defaultValue=None):
        return dict_path_get(self.dict, path, defaultValue)
