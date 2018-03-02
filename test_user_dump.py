#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reddit dump live thread
"""

import argparse
import codecs
import os
from reddit.connections import Reddit
from reddit.endpoints.user import (
    UserInfo, UserAbout, UserInfoBatch)
import json
from ezconf import ConfigFile
import logging


#
#
# program arguments
#
#
parser = argparse.ArgumentParser(description='user info dumper')
parser.add_argument('username', help='reddit username')
#parser.add_argument('output_path', help='path where files will be dumped')
args = parser.parse_args()


#
#
#

def dump_thing(filename, thing):
    with codecs.open(filename, "w", encoding="utf8") as outfile:
        outfile.write(json.dumps(thing.response))


def dump_listing(filename, listing):
    with codecs.open(filename, "w", encoding="utf8") as outfile:
        for item in listing:
            outfile.write(json.dumps(item))
            outfile.write(u"\n")


#
#
# main
#
#

logging.basicConfig(level=logging.DEBUG)

cfg = ConfigFile("config.json")
reddit = Reddit(
    cfg.getValue("auth.client_id"),
    cfg.getValue("auth.client_secret"),
    cfg.getValue("user-agent"))

# dump about first
print "dumping about..."
about = UserAbout(reddit, args.username)
print json.dumps(about.response)


# dump info
print 
#info = UserInfo(reddit, args.username)
#print json.dumps(info.response)


