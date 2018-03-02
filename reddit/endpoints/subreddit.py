#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Live Item endpoints
"""
from ..structures import Listing


"""
Subreddit


"""


class SubredditListing(Listing):
    """
    """

    def __init__(self, connection, subreddit, sort="new", **kwargs):

        super(SubredditListing, self).__init__(
            connection,
            connection.build_oauth_url(
                "r/{}/{}/.json", subreddit, sort),
            **kwargs)
