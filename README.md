confluence-metrics
==================

This application provides way to get Confluence Usage metrics - Atlassian Codegeist 2013

### Postgres Database Setup

* Create Postgres Database to store analyzed log entries.
* NOTE: It's advised you don't use your PRODUCTION JIRA database!

```
createdb -O <jiraowner-E UNICODE <databasename>
createdb -O jira -E UNICODE metricsdb;
```

* Create a table to store logentires;

```
psql metricsdb;

metricsdb=#CREATE TABLE logentries (
    userid character varying(255),
    ipaddress character varying(255),
    actiontype character varying(255),
    useraction character varying(255),
    usersubaction character varying(255),
    unknownactionurl character varying(255),
    spacekey character varying(255),
    title character varying(255),
    pageid character varying(255),
    querystring character varying(255),
    datetimestamp timestamp without time zone,
    actionname character varying(255)
);
```

* That's our setup to store confluence metrics information!

### Confluence Access Log Generation Setup
Refer to this link on how to get this done : https://confluence.atlassian.com/display/CONFKB/How+to+Enable+User+Access+Logging

### Confluence Offline Metrics plugin setup
* Get source from GitHub repository https://github.com/sillycat/confluence-metrics
* It should create directory confluence-metrics and will have these files -> analyze.py, wikiurl.py and logentry.py  and empty "logs" directory.
* Edit analyze.py to enter correct values for database, user, password and host.

### It's time to analyze the metrics
* Copy all altassian-confluence-access.log files that you want to analyze (remember there is one file for each day!) into logs directory.
* For each log file that you want to analyze run following command.

```
    ./analyze.py <log file name>
    ./analyze.py logs/atlassian-confluence-access.log.2013-02-08
    ./analyze.py logs/atlassian-confluence-access.log.2013-02-09
```

P.S.: Please note that application creates intermediate csv file (log.csv) which we later import into database table.

* Please remember if you analyze same log file again, it will add duplicate entries into database.
* verify if entries are created or not

```
    metricsdb=# select count(*) from logentries;
```

### Query to generate chart data
* To get all the pages that got top hits
* To get total view hits per space 

```
metricsdb=> select spacekey || ' - ' || title , count(*) 
from logentries 
where useraction = 'view' and usersubaction='page' and spacekey != '' group by title, spacekey 
order by count(*) desc;

metricsdb=> select spacekey, count(*) 
from logentries 
where spacekey != '' and useraction = 'view'
group by spacekey;
```
<table>
  <tr>
    <th>Page Title</th><th>Hits</th>
  </tr>
  <tr>
    <td>Autodesk 3D Tour</td><td>461</td>
  </tr>
  <tr>
    <td>Challenge Post Wiki - Home Page</td><td>50</td>
  </tr>
  <tr>
    <td>HR Home Page</td><td>24</td>
  </tr>
  <tr>
    <td>AUG - SF Home</td><td>18</td>
  </tr>
  <tr>
    <td>AUG - EBAY Home</td><td>10</td>
  </tr>
</table>

<table>
  <tr>
    <th>Wiki Space</th><th>Page Views</th>
  </tr>
  <tr>
    <td>HOME</td><td>472</td>
  </tr>
  <tr>
    <td>SALES</td><td>147</td>
  </tr>
  <tr>
    <td>HR</td><td>58</td>
  </tr>
  <tr>
    <td>GAMERS</td><td>52</td>
  </tr>
  <tr>
    <td>IT</td><td>25</td>
  </tr>
</table>

### Use this data along with Chart macro to display data in graphical format.

### Contributors
* Raju Kadam

### License
Copyright (c) 2013, Rajendra Kadam, released under a [BSD-style License][lic].
[lic]: http://github.com/sillycat/confluence_metrics_plugin/blob/master/LICENSE.txt
