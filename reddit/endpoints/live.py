#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Live Item endpoints
"""
from ..structures import Thing, Listing


"""
LiveThreadUpdates


"""


class LiveThreadUpdates(Listing):
    """
    """

    def __init__(self, connection, thread_id, **kwargs):

        super(LiveThreadUpdates, self).__init__(
            connection,
            connection.build_oauth_url("live/{}/.json", thread_id),
            **kwargs)


"""
LiveThreadAbout


"""


class LiveThreadAbout(Thing):
    """
    """

    def __init__(self, connection, thread_id, **kwargs):

        super(LiveThreadAbout, self).__init__(
            connection,
            connection.build_oauth_url(
                "live/{}/about.json", thread_id),
            **kwargs)


"""
LiveThreadContributors

"""


class LiveThreadContributors(Listing):
    """
    """

    def __init__(self, connection, thread_id, **kwargs):
        super(LiveThreadContributors, self).__init__(
            connection,
            connection.build_oauth_url(
                "live/{}/contributors.json", thread_id),
            **kwargs)


"""
LiveThreadDiscussions

"""


class LiveThreadDiscussions(Listing):
    """
    """

    def __init__(self, connection, thread_id, **kwargs):
        super(LiveThreadDiscussions, self).__init__(
            connection,
            connection.build_oauth_url(
                "live/{}/discussions.json", thread_id),
            **kwargs)
