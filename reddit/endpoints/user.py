#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Live Item endpoints
"""
from ..structures import Thing, Listing


"""
LiveThreadUpdates


"""


class UserInfo(Listing):
    """
    """

    def __init__(self, connection, username, **kwargs):

        super(UserInfo, self).__init__(
            connection,
            connection.build_oauth_url("user/{}/.json", username),
            **kwargs)


"""
UserAbout


"""


class UserAbout(Thing):
    """
    """

    def __init__(self, connection, username, **kwargs):

        super(UserAbout, self).__init__(
            connection,
            connection.build_oauth_url(
                "user/{}/about.json", username),
            **kwargs)





