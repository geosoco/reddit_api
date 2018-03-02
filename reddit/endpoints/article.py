#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Article
"""

from ..utils import DictAccessor
from ..structures import Thing, Listing

"""
Article


"""


class Article(Thing):
    """
    """

    def __init__(
            self, connection, thread_id=None,
            depth=10, limit=200, from_json=None, **kwargs):

        self.depth = depth
        self.limit = limit
        self.thread_id = thread_id

        self._clear()


        super(Article, self).__init__(
            connection,
            connection.build_oauth_url("comments/{}/.json", thread_id),
            params={"depth": depth, "limit": limit},
            **kwargs)

        self.parse_response(self.response)

    def _clear(self):
        self.data = None
        self.comments = None


    def parse_response(self, response):
        if response is None or len(response) < 2:
            self._clear()
            print "response is invalid:", response
            return

        for obj in response:
            oa = DictAccessor(obj)

            # verify its a listing
            kind = oa.get("kind")
            if kind is None or kind.lower() != "listing":
                print "obj is not a Listing!"
                continue

            # check the child kind of the first item
            child_kind = oa.get("data.children.0.kind")

            # is it article data?
            if child_kind == "t3":
                self.data = oa.get("data.children.0")
                print "Got ", repr(self.data)
            # comments?
            elif child_kind == "t1":
                self.comments = CommentListing(
                    self.connection,
                    self,
                    depth=self.depth,
                    limit=self.limit,
                    from_json=obj)




class CommentListing(Listing):
    """
    """

    def __init__(
            self, connection,
            article,
            depth=10, limit=200,
            from_json=None, **kwargs):

        self.article = article
        self.thread_id = self.article.thread_id
        self.depth = depth
        self.limit = limit

        self.more_params = {
            "api_type": "json",
            "link_id": "t3_" + self.thread_id
        }

        self._more_children_endpoint = self.article.connection.build_oauth_url(
            "api/morechildren.json")

        self._comment_dict = {}
        self._more_children_set = set()
        self._retry_ids = set()

        if from_json is not None:
            self.response = from_json
            da = DictAccessor(self.response)

            assert da.get("kind") == "Listing", "JSON not a listing"
            children = da.get("data.children")
            assert children is not None, "Children is None"

            self.parse_comment_block(children)


    def flatten_children(self, children, flattened=None):
        _flattened = flattened if flattened is not None else []

        for child in children:
            # append child to list
            _flattened.append(child)

            da = DictAccessor(child)

            kind = da.get("kind", "").lower()
            #print "flatten - kind: ", kind
            #print "flatten - id: ", da.get("data.id")
            if kind == "t1":
                replies = da.get("data.replies")
                if (
                        replies is not None and
                        not isinstance(replies, basestring) and
                        da.get("data.replies.kind") == "Listing"):

                    # step through grandchildren
                    grand_children = da.get("data.replies.data.children")
                    if grand_children is not None:
                        self.flatten_children(grand_children, _flattened)


        return _flattened


    def split_flattened_comments(self, flattened_list):
        if flattened_list is None:
            return []

        ret_ids = []

        for c in flattened_list:
            da = DictAccessor(c)
            kind = da.get("kind")
            id = da.get("data.id")
            ret_ids.append(id)

            #print "kind: ", kind, "   id: ", id
            assert id is not None and len(id) > 0, "id is invalid"

            if kind == "t1":
                self._comment_dict[id] = c
            elif kind == "more":
                self.append_more_comment_obj(c)

        return ret_ids


    def append_more_comment_obj(self, block):
        if block is None:
            return

        da = DictAccessor(block)
        children = da.get("data.children")

        for child in children:
            self._more_children_set.add(child)


    def parse_comment_block(self, children):
        if children is None:
            print "children is None"
            return

        flattened = self.flatten_children(children)

        self.split_flattened_comments(flattened)


    def flatten_more_comment_block(self, more_obj):
        da = DictAccessor(more_obj)
        things = da.get("json.data.things")

        if things is None:
            print "Error: things is none"
            print more_obj
            return []
        else:
            print "flattening more comments: ", len(things)

        if len(things) == 0:
            print "no things!"


        return self.split_flattened_comments(things)


    def choose_more_comments(self, n=5):
        max_n = min(n, len(self._more_children_set))
        ret = []

        while len(ret) < max_n and len(self._more_children_set) > 0:
            id = self._more_children_set.pop()
            # make sure we haven't requested it already
            if id in self._comment_dict:
                continue

            ret.append(id)

        return ret


    def request_more_comments(self, comment_ids=None, update_retries=True):
        if comment_ids is None:
            more_comment_ids = self.choose_more_comments()
        else:
            more_comment_ids = comment_ids

        self.more_params["children"] = ",".join(more_comment_ids)
        print "requesting ids: ", more_comment_ids
        #print "requesting more with these params"
        #print self.more_params
        response = self.article.connection.get(
            self._more_children_endpoint,
            params=self.more_params)

        if response is not None:
            # print response.json()
            got_ids = self.flatten_more_comment_block(response.json())
            if update_retries:
                unreturned = set(more_comment_ids) - set(got_ids)
                print "unreturned: ", unreturned
                self._retry_ids |= unreturned
        else:
            print "Error requesting more..."


    def request_all_comments(self):
        cnt = 0
        while len(self._more_children_set) > 0:
            self.request_more_comments()
            cnt += 1

            print "step {} (comments {}, mores {}, retries {})".format(
                cnt,
                len(self._comment_dict),
                len(self._more_children_set),
                len(self._retry_ids))

            # retry the fails
            while len(self._retry_ids) > 0:
                id = self._retry_ids.pop()
                self.request_more_comments(comment_ids=[id], update_retries=False)

                print "id {} (comments {}, mores {}, retries {})".format(
                    id,
                    len(self._comment_dict),
                    len(self._more_children_set),
                    len(self._retry_ids))



    def _request_retries_broken(self):
        thread = DictAccessor(self.article.data)
        subreddit_name = thread.get("subreddit")
        for id in self._retry_ids:
            # make sure we haven't requested it already
            if id in self._comment_dict:
                continue

            print "id {} (comments {}, mores {}, retries {})".format(
                id,
                len(self._comment_dict),
                len(self._more_children_set),
                len(self._retry_ids))

            # this needs to not be an oauth url, but a normal one
            #
            endpoint = self.article.connection.build_oauth_url(
                "r/{}/comments/{}/comments/{}.json",
                subreddit_name, self.thread_id, id)

            resp = self.article.connection.get(
                endpoint, params={"limit": 500, "depth": 20})

            print "url: ", resp.url
            print resp.status_code

            if resp is not None:
                da = DictAccessor(self.response)

                children = da.get("data.children")
                #print "children: ", children
                self.parse_comment_block(children)




class Comment(Thing):
    """
    Simple comment
    """

    def __init__(
            self, connection, thread_id,
            from_json=None, **kwargs):
        if from_json is None:
            super(Article, self).__init__(
                connection,
                connection.build_oauth_url("comments/{}/.json", thread_id),
                params={"depth": 1, "limit": 2},
                **kwargs)