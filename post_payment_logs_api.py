#!/usr/bin/python

from requests import get, post, auth
import json
import os

KEYS = ['id', 'config', 'event', 'httpVersion', 'instance', 'labels', 'log', 'method', 'path', 'pid', 'query', 'responseSentTime', 'responseTime', 'route', 'source', 'statusCode', 'tags', 'timestamp']

def binary_search(array, target, left, right):
	if left > right:
		return -1
	middle = (left + right) / 2
	data = json.loads(array[middle])
	if data['timestamp'] < target:
		left = middle + 1
		return binary_search(array, target, left, right)
	if data['timestamp'] > target:
		right = middle - 1
		return binary_search(array, target, left, right)
	if data['timestamp'] == target:
		return middle


def get_latest_file():
	files = []
	path = "/data/payment/logs/api"
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			files.append(file)
	return os.path.join(path, sorted(files, reverse=True)[0])


def post_data():

	api_log_file = (get_latest_file())
	print (api_log_file)

	with open(api_log_file, 'r') as f:
		lines = f.readlines()

		# GET the last index of api logs
		lastDBRecord = get('http://elasticsearch.member.id/payment_logs/api/_search?from=0&size=1', auth=auth.HTTPBasicAuth('admin','password'))
		lastDBRecord = json.loads(lastDBRecord.text)
		try:
			dbIndex = int(lastDBRecord['hits']['total'])  # index of last elasticsearch record

			# Get the last timestamp of the last elasticsearch record 
			lastData = get('http://elasticsearch.member.id/payment_logs/api/' + str(dbIndex), auth=auth.HTTPBasicAuth('admin','password'))
			lastData = json.loads(lastData.text)
			lastTimestamp = lastData['_source']['timestamp']
		except Exception as e:
			dbIndex = 1
			print (e)

		dataIndex = binary_search(lines, lastTimestamp, 0, len(lines)-1) + 1
		print (dbIndex, dataIndex, lastTimestamp)

		# Insert all new data into elasticsearch
		for line in lines[dataIndex:]:
			data = json.loads(line.strip('\n'))
			URL = 'http://elasticsearch.member.id/payment_logs/api/' + str(dbIndex)
			response = post(URL, auth=auth.HTTPBasicAuth('admin', 'password'), json=data)
			print (response.text)
			dbIndex += 1

if __name__ == '__main__':
	post_data()
