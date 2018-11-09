#!/usr/bin/env python

import argparse
import json
import urllib.request

parser = argparse.ArgumentParser(description="rspamd web interface statistic fetcher for InfluxDB usage")
parser.add_argument("--url", action="store", help="URL to rspamd web interface installation")
parser.add_argument("--password", action="store", help="Password for API authentication (same as for graphical login)")
parser.add_argument("--config", action="store", help="Path to the configuration file for the application to use")

args = parser.parse_args()

# Perform some stupid basic validation on the arguments
if (args.url is None and args.password is None) and args.config is None:
    parser.error("Please provide --url and --password arguments or the path to a configuration file using --config")

if (args.url is None and args.password is not None) or (args.url is not None and args.password is None):
    parser.error("Please use --url with the --password argument and way round. You may provide the path to a "
                 "configuration file by only using the --config argument.")

if args.url is not None and args.password is not None and args.config is not None:
    parser.error("Please provide whether --url and --password arguments *or* --config argument.")

if args.config is not None and (args.url is not None or args.password is not None):
    parser.error("Please provide whether --url and --password arguments *or* --config argument.")

# Basic variable initialization
url = None
password = None

# Read variables from file if necessary
if args.config is not None:
    data = None

    try:
        fh = open(args.config, "r")
        data = json.load(fh)
    except IOError as e:
        parser.error("Could not read JSON config from file. Received IOError: " + str(e))

    if data is not None and ("url" not in data or "password" not in data):
        parser.error("Could not read URL and password from JSON configuration. Please see documentation for correct "
                     "configuration file formatting.")
    elif data is None:
        parser.error("Something went wrong during parsing of JSON configuration file. Please check your configuration!")
    else:
        url = data['url']
        password = data['password']
else:
    # Read variable from args
    url = args.url
    password = args.password

# Make sure we got the trailing slash at the URL
if str.endswith(url, "/"):
    fetch_url = url + "stat?password=" + urllib.parse.quote_plus(password)
else:
    fetch_url = url + "/stat?password=" + urllib.parse.quote_plus(password)

try:
    resp = urllib.request.urlopen(fetch_url)
except Exception:
    print("Could not send GET request to given URL. Check url parameter!")
    exit(1)

# Authorization failed
if resp.code == 403:
    print("Authorization with rspamd web interface failed. Check password parameter!")
    exit(1)

elif resp.code == 404:
    print("HTTP server returned HTTP status code 404. Check url parameter!")
    exit(1)

elif resp.code == 200:
    # Successful call
    json = json.loads(resp.read().decode('utf-8'))

    action_reject = str(json["actions"]["reject"]) + "i"
    action_soft_reject = str(json["actions"]["soft reject"]) + "i"
    action_rewrite = str(json["actions"]["rewrite subject"]) + "i"
    action_add_header = str(json["actions"]["add header"]) + "i"
    action_greylist = str(json["actions"]["greylist"]) + "i"
    action_no_action = str(json["actions"]["no action"]) + "i"

    # Build InfluxDB Line protocol compatible output
    print(
        "rspamd_actions reject={0},soft_reject={1},rewrite_subject={2},add_header={3},greylist={4},no_action={5}".format(
            action_reject, action_soft_reject, action_rewrite, action_add_header, action_greylist, action_no_action))

    stat_scanned = str(json["scanned"]) + "i"
    stat_learned = str(json["learned"]) + "i"
    stat_spam_count = str(json["spam_count"]) + "i"
    stat_ham_count = str(json["ham_count"]) + "i"
    stat_connections = str(json["connections"]) + "i"
    stat_control_connections = str(json["control_connections"]) + "i"
    stat_pools_allocated = str(json["pools_allocated"]) + "i"
    stat_pools_freed = str(json["pools_freed"]) + "i"
    stat_bytes_allocated = str(json["bytes_allocated"]) + "i"
    stat_chunks_allocated = str(json["chunks_allocated"]) + "i"
    stat_chunks_freed = str(json["chunks_freed"]) + "i"
    stat_chunks_oversized = str(json["chunks_oversized"]) + "i"
    stat_fragmented = str(json["fragmented"]) + "i"
    stat_total_learns = str(json["total_learns"]) + "i"
    stat_fuzzy_rspamd = str(json["fuzzy_hashes"]["rspamd.com"]) + "i"

    print("rspamd_stats scanned={0},learned={1},spam_count={2},ham_count={3},connections={4},control_connections={5},"
          "pools_allocated={6},pools_freed={7},bytes_allocated={8},chunks_allocated={9},chunks_freed={10},"
          "chunks_oversized={11},fragmented={12},total_learns={13},fuzzy={14}".format(stat_scanned, stat_learned,
                                                                                      stat_spam_count,
                                                                                      stat_ham_count,
                                                                                      stat_connections,
                                                                                      stat_control_connections,
                                                                                      stat_pools_allocated,
                                                                                      stat_pools_freed,
                                                                                      stat_bytes_allocated,
                                                                                      stat_chunks_allocated,
                                                                                      stat_chunks_freed,
                                                                                      stat_chunks_oversized,
                                                                                      stat_fragmented,
                                                                                      stat_total_learns,
                                                                                      stat_fuzzy_rspamd))

    exit(0)

else:
    print("Web request returned unhandled HTTP status code " + str(resp.code) + ". Please open an issue at GitHub "
                                                                                "with further details.")
    exit(1)
