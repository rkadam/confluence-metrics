#!/usr/bin/env python

"""
logentry.py

Class that implements the data structure of an Apache Combined Log Format (CLF) log entry
Sample log line ->
2013-02-08 07:29:34,845 INFO [TP-Processor3] [atlassian.confluence.util.AccessLogFilter] doFilter rkadam https://pandapedia.savagebeast.com/display/HOME/home 1725173-3259 81 172.17.250.184
"""

import datetime
import re
import time


class LogEntry:

    p = re.compile('([0-9]{4}):24:')


    def __init__(self, line):
        fields = line.split()

        self.datestamp = fields[0]                                          # e.g. 2013-02-08
        self.timestamp = fields[1].split(',')[0]                            # e.g. 07:29:34
        self.datetimestamp = self.datestamp + " " + self.timestamp          # e.g. 2013-02-08 07:29:34

        self.logpriority = fields[2]                                        # e.g. INFO
        self.threadname = fields[3][1:-1]                                   # e.g. [TP-Processor3]
        self.logcategoryname = fields[4][1:-1]                              # e.g. [atlassian.confluence.util.AccessLogFilter]
        self.logmethodname = fields[5]                                      # e.g. doFilter
        self.userid = fields[6]                                             # e.g. rkadam

        # When store denormalize log data into comma separated csv file.
        # Hence we have to encode all commas in url otherwise csv file will treat them as separator.
        # So replace all occurrances of commas with corresponding URL encoding string "%2C"
        self.url = fields[7]                                                # e.g. https://pandapedia.savagebeast.com/display/HOME/home

        """
        Base URL can be https://pandapedia.savagebeast.com
                        or https://wiki.savagebeast.com
                        or https://intranet.savagebeast.com
        and for DEV / STAGE instances it can be
                        or https://wiki-dev.savagebeast.com
                        or https://pandapedia-4-dev.savagebeast.com
                        or https://pandapedia-stage.savagebeast.com
                        and so on.
        So we would like to capture this BASE URL as a separate entry into log URL. and relative URL (/display/HOME) as different parameters.

        Solution to extract base URL and relative URL: http://stackoverflow.com/questions/8170982/strip-string-after-third-occurrence-of-character-python
        We know that URL will always have at least two "/" example: https://pandapedia/display/HOME or https://pandapedia.savagebeast.com/display/HOME and so on.
        So we will split string using "/" as separator. Third element will be base url and 4th onwards be relative url.
        Hence we will join 4th and all elements after that to form a relative URL.
        """
        urltokens = self.url.split("/")
        self.baseurl = urltokens[2]                                         # e.g. panapedia.savagebeast.com
        self.relativeurl = "/".join(urltokens[3:])                          # e.g. display/HOME/home

        self.memorylog = fields[8]                                          # e.g. 1725173-3259
        self.querytime = fields[9]                                          # e.g. 81
        self.ipaddress = fields[10]                                         # e.g. 172.17.250.184

    def __repr__(self):
        return "<LogEntry: datestamp=%s, timestamp=%s, datetimestamp=%s, logpriority=%s, threadname=%s, logcategoryname=%s, logmethodname=%s, userid=%s, url=%s, baseurl=%s, relativeurl=%s, memorylog=%s, querytime=%s, ipaddress=%s>" % (self.datestamp, self.timestamp, self.datetimestamp, self.logpriority, self.threadname, self.logcategoryname, self.logmethodname, self.userid, self.url, self.baseurl, self.relativeurl, self.memorylog, self.querytime, self.ipaddress)

    def getTimestamp(self):
        entrytime = datetime.datetime(*time.strptime(self.datetimestamp, "%Y-%m-%d %H:%M:%S")[0:6])
        return entrytime
