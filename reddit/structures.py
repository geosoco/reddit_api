#!/usr/bin/env python
#
"""
Reddit objects
"""

import requests
import logging



log = logging.getLogger(__file__)

"""
==========================================================================

Thing


==========================================================================

"""


class Thing(object):
    """
    Wrapper for a thing object
    """

    def __init__(self, connection, endpoint, delay_request=False, **kwargs):
        self.params = kwargs.pop("params", {})
        self.response = None
        self.error = None
        self.connection = connection
        self.endpoint = endpoint

        if not delay_request:
            self.make_request()

    def make_request(self):
        #print "thing request", self.endpoint
        response = self.connection.get(
            self.endpoint,
            params=self.params
            )

        #print response.status_code

        if response.status_code == requests.codes.ok:
            self.response = response.json()
            self.error = None
            #print "response: ", self.response
        else:
            self.response = None
            log.error("Request error ({}, {}, {})".format(
                self.endpoint, response.status_code, response.text
            ))

            self.error = {
                "status": response.status_code,
                "text": response.text
            }



"""
==========================================================================

Listing


==========================================================================
"""


class Listing(object):
    """
    Wrapper for a listing object
    """

    def __init__(self, reddit, endpoint, limit=100, params=None):
        default_params = {
            "after": "",
            "before": "",
            "limit": limit
        }

        if params is not None:
            self.params = dict(default_params, **params)
        else:
            self.params = default_params

        self.connection = reddit
        self.endpoint = endpoint
        self.response = None
        self.resp_index = 0

    def make_request(self):
        print "listing request", self.endpoint
        response = self.connection.get(
            self.endpoint,
            params=self.params)
        self.resp_index = 0

        if response.status_code == requests.codes.ok:
            self.response = response.json()
        else:
            print "listing error response", response.status_code
            self.response = None

    def next_page(self):
        """ """

        self.params["after"] = ""

        if self.response is not None:
            data = self.response.get("data", None)
            if data is not None:
                # if we already have a response, and we have an after
                # field, use that as a parameter in the request
                after = data.get("after", None)

                if after is None:
                    return False
                self.params["after"] = after

        self.params["before"] = ""
        self.make_request()

        return (self.response is not None)

    def __iter__(self):
        """ implements iterator protocol. """
        self.response = None
        self.resp_index = 0
        return self

    def next(self):
        """ returns next object. """
        # if we don't have a response, grab one
        if self.response is None:
            if not self.next_page():
                raise StopIteration()

        data = self.response.get("data", {})
        children = data.get("children", {})

        # do we need to move to the next page?
        if self.resp_index >= len(children):
            if not self.next_page():
                raise StopIteration

        # make sure we're still within range
        if self.resp_index < len(children):
            list_item = children[self.resp_index]
            self.resp_index += 1
            return list_item

        raise StopIteration()
