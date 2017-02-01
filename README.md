# virginmediahub3-stats

## Purpose 
This is a python script to grab connection status data from your VirginMedia (formally UPC) Hub 3.0 cabel modem.
By default the data is sent to your InfluxDB database for consumption by Grapaha, ideally your cron job this every hour or so.

Alternatively the script can be run with `-c` parameter to get dump to current statistics to standard out for those 'crap whats up with the internet(!?) moments'

## Requirements
* VirginMedia Hub 3.0 router
* InfluxDB database


## InfluxDB 
### Schema
  
| Measurement   | Tag           | Fields         |
| ------------- | ------------- | ------------- |
| downstream    | channel       | power, snr |
| upstream      | channel       | power |

### Create database
```
$ influxdb localhost
> create database virginmediahub
```

