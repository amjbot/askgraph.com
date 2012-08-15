#!/usr/bin/env python

import noisebot

i = noisebot.crawl()

import syslog
syslog.syslog( syslog.LOG_INFO, "crawled %d websites" % i )
