# rspamd-influxdb
Quick and dirty approach to get stats of rspamd out of the webinterface's API into InfluxDB for visualizing using Grafana.

## Usage
`python3 rspamd-influxdb.py https://example.com:1337/ superSecretPassword`

## Utilization
Use this script call within InfluxData's Telegraf

e.g.:
```
[[inputs.exec]]
	commands = ["python3 /opt/rspamd-influxdb/rspamd-influxdb.py http://localhost:11334/ superSecretPassword"]
	timeout = "5s"
	data_format = "influx"
```

## Grafana example
![Grafana Example](https://raw.githubusercontent.com/thannaske/rspamd-influxdb/master/grafana-example.png)
