#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
It Item endpoints
"""
from ..structures import Thing, Listing


"""
Submission


"""


class Submission(Thing):
    """
    """

    def __init__(self, connection, id, **kwargs):
        super(Submission, self).__init__(
            connection,
            connection.build_oauth_url(
                "/comments/{}", id, id, *kwargs)
            )


class ByIdListing(Listing):
    """
    """

    def __init__(self, connection, names, **kwargs):

        super(ByIdListing, self).__init__(
            connection,
            connection.build_oauth_url(
                "by_id/{}.json", ",".join(names)),
            **kwargs)
        self.make_request()
