#!/usr/bin/env python
#
"""
Reddit connection
"""

from datetime import datetime, timedelta
import time
import requests
import requests.auth



REDDIT_CLIENT_AUTH_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_OAUTH_ENDPOINT_BASE = "https://oauth.reddit.com/"

_headers = {
    'User-Agent': 'Mac OSX:com.emcomp.smcap:0.1 /u/geosoco'
}

#
#
#
#
#


class RateLimiter(object):
    """
    Rate limiter class
    """

    def __init__(
            self,
            num_requests=1,
            duration_window=timedelta(seconds=60)):
        self.num_requests = num_requests
        self.duration = duration_window
        self.request_list = []

    def last_time(self):
        return self.request_list[0] if len(self.request_list) > 0 else None

    def add_request(self):
        """ add a new request """
        self.request_list.append(datetime.now())

    def remove_old_requests(self):
        """ Remove all requests older than our window. """
        # calculate our cutoff date
        cutoff_date = datetime.now() - self.duration
        # while the list is long enough
        while (len(self.request_list) > 0 and
               self.request_list[0] < cutoff_date):
            self.request_list.pop(0)

    def is_ratelimited(self):
        """ return true if currently rate limited. """
        # first remove old ones
        self.remove_old_requests()

        return len(self.request_list) >= self.num_requests

    def get_delta_before_next_request(self):
        """
            returns the number of seconds until a new request
            can be made.
        """

        # check if we're rate limited, and clear our queue
        if not self.is_ratelimited():
            return 0

        # grab last time in the queue
        last_time = self.last_time()
        if last_time is None:
            return timedelta(seconds=0)

        # calculate wait time
        wait_time = self.duration - (datetime.now() - last_time)

        return wait_time.total_seconds()

    def wait_until_ready(self):
        """ waits until rate limit has passed. """

        wait_time = self.get_delta_before_next_request()

        # sleep
        time.sleep(wait_time)

    def check_and_wait(self):
        """ checks if rate limited, and waits if necessary. """

        if self.is_ratelimited():
            #print "waiting {} seconds".format(
            #    self.get_delta_before_next_request())
            self.wait_until_ready()


"""
==========================================================================

OAuthConnection


==========================================================================
"""


class OAuthConnnection(object):
    """
    Simple OAuth connection for reddit
    """

    def __init__(self, client_id, client_secret, user_agent):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_type = None
        self.access_token = None
        self.auth = None
        self.headers = {
            'User-Agent': user_agent
        }

        self.connected = False

        self.connect()
        self.rate_limiter = RateLimiter(num_requests=60)

    def is_connected(self):
        """ Returns true if connected. """
        return self.connected

    def build_auth(self):
        """ build request auth obj. """

        # if one already exists, ignore
        if self.auth is not None:
            return

        # build basic one
        self.auth = requests.auth.HTTPBasicAuth(
            self.client_id,
            self.client_secret)

    def request_auth_token(self):
        """ makes a request for the auth token. """

        # XXX TODO
        # THIS NEEDS TO BE ABLE TO RENEW THE TOKEN
        resp = requests.post(
            REDDIT_CLIENT_AUTH_URL,
            auth=self.auth,
            headers=self.headers,
            data={
                "grant_type": "client_credentials",
                "device_id": "DO_NOT_TRACK_THIS_DEVICE"
                }
            )

        # XXX TODO -- CHECK FOR ERRORS

        json_resp = resp.json()
        token_type = json_resp["token_type"]
        access_token = json_resp["access_token"]

        #print "access: ", token_type, access_token

        # update our headers
        self.headers["Authorization"] = u"%s %s" % (token_type, access_token)

        self.connected = True

    def connect(self):
        """ connects. """
        self.build_auth()
        self.request_auth_token()

    def reconnect(self):
        """ reconnects. """
        self.auth = None
        self.connect()

    def get(self, url, **kwargs):
        #print "oauthconnection - get"
        if not self.is_connected():
            self.connect()

        # first merge headers
        kw_headers = kwargs.pop("headers", {})
        headers = dict(self.headers, **kw_headers)

        #print "headers: ", headers

        # XXX HACK
        # REMOVE and use the rate limiter, after it supports
        # some progressive

        self.rate_limiter.check_and_wait()

        resp = requests.get(url, headers=headers, **kwargs)
        if resp is not None:
            if resp.status_code == 401:
                print "request returned 401"
                print resp.headers
                self.reconnect()

            if resp.headers is not None:
                #print resp.headers
                used = resp.headers.get("X-Ratelimit-Used", None)
                remain = resp.headers.get("X-Ratelimit-Remaining", None)
                end = resp.headers.get("X-Ratelimit-Reset", None)

                #if used is None and remain is None and end is None:
                #    print resp.headers
                #else:
                if used is not None or remain is not None or end is not None:
                    print "request[ used: {}, remain: {}, end: {}]".format(
                        used, remain, end)
                    if remain is not None and int(remain) < 1:
                        print "rate limited for {} seconds. sleeping.".format(
                            end)
                        time.sleep(int(end))

        self.rate_limiter.add_request()


        #time.sleep(1)

        return resp


"""
==========================================================================

RedditConnection


==========================================================================
"""


class Reddit(object):
    """

    """

    def __init__(self, client_id, client_secret, user_agent):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.oauth_connection = None
        self.oauth_endpoint_base = REDDIT_OAUTH_ENDPOINT_BASE

    def connect(self):
        #
        self.oauth_connection = OAuthConnnection(
            self.client_id,
            self.client_secret,
            self.user_agent)

    def is_connected(self):
        return self.oauth_connection is not None

    def get(self, endpoint, **kwargs):
        if (self.oauth_connection is None):
            self.connect()

        return self.oauth_connection.get(
            endpoint,
            **kwargs)

    def get_listing(self, url):
        pass


    def build_oauth_url(self, endpoint, *args, **kwargs):
        return (self.oauth_endpoint_base + endpoint).format(
            *args,
            **kwargs)



#
#
#
# temporary main with tests
#
#

def run_rl_test(name, callback, **kwargs):
    print "Running %24s...  " % (name), 
    try:
        rl = RateLimiter(**kwargs)
        callback(rl)
#    except AssertionError, e:
#        print "failed"
#        print 
#        return
    except Exception, e:
        print "failed"
        print "Exception: ", e
        return
    print "passed"

def run_default_rl_test(name, callback):
    run_rl_test(
        name,
        callback,
        num_requests=2,
        duration_window=timedelta(seconds=10))

def test_construction(rl):
    assert rl.num_requests == 2, "Num requests uninitialized"
    assert rl.duration.total_seconds() == 10, "duration not correct"
    assert rl.request_list is not None, "Request list uninitialized"


def test_lasttime_correct(rl):
    dt = datetime.now()
    rl.add_request()
    delta = dt - rl.last_time()
    assert delta.total_seconds() <= 1, "Invalid last time"

def test_delta_time(rl):
    delta = rl.get_delta_before_next_request()
    assert delta == 0, "initial delta not zero (%f)" % (delta)

    # add a request and check
    rl.add_request()
    delta = rl.get_delta_before_next_request()
    assert delta == 0, \
        "delta zero after first request (%f)" % (delta)

    # add another request
    rl.add_request()
    delta = rl.get_delta_before_next_request()
    assert (delta > 8 and delta < 10), \
        "delta after second request (%f)" %(delta)

    # wait 5 seconds and
    time.sleep(5)
    delta = rl.get_delta_before_next_request()
    assert (delta > 3.7 and delta < 5), \
        "delta after 5 sec pause request (%f)" %(delta)

    # wait 5 seconds and
    time.sleep(5)
    delta = rl.get_delta_before_next_request()
    assert len(rl.request_list) == 0, \
        "asssert all requests removed from list (%d)" % (
            len(rl.request_list))
    assert (delta == 0), \
        "delta after 10 sec pause request (%f)" %(delta)


def test_wait_until_ready(rl):
    """ tests that wait_until_ready works. """
    # fill up default request list with 2 requests
    rl.add_request()
    rl.add_request()

    dt_start = datetime.now()
    rl.wait_until_ready()

    # calculate delta time and assert
    delta = dt_start - datetime.now()
    assert (delta > 9.8 and delta < 11), "waited too long"

def run_tests():
    run_default_rl_test("Construction", test_construction)
    run_default_rl_test("last time", test_lasttime_correct)
    run_default_rl_test("delta before request", test_delta_time)
    run_default_rl_test("wait time", test_delta_time)


if __name__ == "__main__":
    run_tests()
