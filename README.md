# rspamd-influxdb
Quick and dirty approach to get stats of rspamd out of the webinterface's API into InfluxDB for visualizing using Grafana.

## Usage
`python3 rspamd-influxdb.py https://example.com:1337/ superSecretPassword`

## Utilization
Use this script call within InfluxData's Telegraf
