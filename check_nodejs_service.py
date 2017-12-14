#!/usr/bin/python

"""
Prometheus client library to check if certain pm2 process is running 
The client listen on port 9101
Coded based on https://github.com/prometheus/client_python
Written by Steven Stevanus (https://github.com/stvnorg)
"""

from prometheus_client import Gauge, start_http_server
import random
import time
import os

app_memberarea_staging = Gauge('app_memberarea_staging_status', 'Status of app-memberarea port 6767')
app_publicapi_staging = Gauge('app_publicapi_staging_status', 'Status of app-publicapi port 7070')
app_publicapi_production = Gauge('app_publicapi_production_stage_status', 'Status of app-production port 5050')
app_payment_staging = Gauge('app_payment_staging_status', 'Status of npm port 9000')

@app_memberarea_staging.time()
@app_publicapi_staging.time()
@app_publicapi_production.time()
@app_payment_staging.time()
def process_request(t):

	PORTS = ['6767', '7070', '5050', '9000']
	PROCESS = [app_memberarea_staging, app_publicapi_staging, app_publicapi_production, app_payment_staging]

	# Check all the services status
	for i in range(len(PROCESS)):
		checkPort = os.popen('sudo netstat -tulpn | grep ' + PORTS[i])
		if (len(checkPort.readlines())):
			PROCESS[i].set(1)
		else:
			PROCESS[i].set(0)

	# Check app_memberarea_staging status
	#checkPort = os.popen('sudo netstat -tulpn | grep 6767')
	#if (not len(checkPort.readlines())):
	#	app_memberarea_staging.set(0)
	#else:
	#	app_memberarea_staging.set(1)

	time.sleep(t)

if __name__ == '__main__':
	# Start up the server to expose the metrics.
	start_http_server(9101)
	# Generate some requests.
	while True:
		process_request(5)
