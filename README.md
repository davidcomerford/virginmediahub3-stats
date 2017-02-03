# virginmediahub3-stats

## Purpose 
This is a python script to grab connection status data from your VirginMedia (formally UPC) Hub 3.0 cable modem.
By default the data is sent to your InfluxDB database for consumption by Grapaha, ideally your cron job this every hour or so.

Alternatively the script can be run with `-c` parameter to get dump to current statistics to standard out for those 'crap whats up with the internet(!?) moments'

## Requirements
* VirginMedia Hub 3.0 router
* Python >= 2.7
* Requests Python library (pip install requests)
* InfluxDB database (optional)
* Grapana (optional)


## InfluxDB 
### Schema
  
| Measurement   | Tag           | Fields     |
| ------------- | ------------- | ------------- |
| downstream    | channel       | power, snr |
| upstream      | channel       | power      |
| status        | state         |            |

### Create database
Note: I've created a retention policy of 365 days here.

Probably the smart thing to do here is lower that value and create a CQ for longer term downsampled storage. 
```
$ influxdb localhost
> CREATE DATABASE virginmediahub
> CREATE RETENTION POLICY "one-year" ON "virginmediahub" DURATION 365d REPLICATION 1 DEFAULT
```

### Install
git clone https://github.com/davidcomerford/virginmediahub3-stats.git

chmod +x virginmediahub-stats.py

cp virginmediahub-stats.py /etc/cron.hourly/

## Graphana Queries
#### Provisioned state
```
SELECT last("state") FROM "status" WHERE $timeFilter GROUP BY time($interval)
```

#### Downstream power 
```
SELECT mean("power") FROM "autogen"."downstream" WHERE $timeFilter GROUP BY time($interval), "channel" fill(previous)
```
#### Downstream signal to noise ratio
```
SELECT last("snr") FROM "downstream" WHERE $timeFilter GROUP BY time($interval), "channel" fill(previous)
```
#### Upstream power
```
SELECT last("power") FROM "upstream" WHERE $timeFilter GROUP BY time($interval), "channel" fill(previous)
```