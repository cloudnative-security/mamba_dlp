#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import sys
import boto3
import time
import json
import argparse
import logging


import data_source
import data_finders
import aws
import state_object

def lambda_handler(event, context):
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	conf_file = "conf/cloud_dlp.conf"
	config = load_conf(conf_file)
	#Read event
	for record in event['Records']:
		aws_account='523256993465'
		bucket=record['s3']['bucket']['name']
		key=record['s3']['object']['key']
		object_id=aws_account + ":" + bucket + ":" + key
		#build object to scan
		object_to_scan={'objects':[]}
		object_to_scan['objects'].append({'object_id' : object_id,
                         'object_type' : 's3',
                         'aws_account': aws_account,
                         'bucket': bucket, 
                         'key': key
                        }
                        )
                
	print(json.dumps(object_to_scan , sort_keys=True , indent=2))
	#run scan
	state = state_object.sensitive_data(config['global_conf']['dynamo_table'])
	scan_result = scan_single_object(config , state , json.dumps(object_to_scan))
	print("Sensitive Data Found:")
	print(json.dumps(scan_result , sort_keys=True , indent=2))

	return

def display_banner():


    print(" _____ _                 _      _ _       ")
    print("/  __ \ |               | |    | | |      ")
    print("| /  \/ | ___  _   _  __| |  __| | |_ __  ")
    print("| |   | |/ _ \| | | |/ _` | / _` | | '_ \ ")
    print("| \__/\ | (_) | |_| | (_| || (_| | | |_) |")
    print(" \____/_|\___/ \__,_|\__,_| \__,_|_| .__/ ")
    print("                        ______     | |    ")
    print("                       |______|    |_|  	 ")

    return

def load_conf(conf_file_location):
		conf_file= open(conf_file_location,'r')
		conf=json.load(conf_file)

		return conf

def full_scan(config , state ):

	finder = data_finders.finder(config['global_conf']['dynamo_table'])
	s3 = data_source.s3(config['global_conf']['aws_accounts'] , config['global_conf']['aws_role'])
	s3.objects = s3.find_objects()
	sesitive_data = finder.scan_objects(s3)

	return sesitive_data

def scan_single_object(config , state ,  object):
	finder = data_finders.finder(config['global_conf']['dynamo_table'])
	s3 = data_source.s3(config['global_conf']['aws_accounts'] , config['global_conf']['aws_role'])
	s3.objects = json.loads(object)
	sesitive_data = finder.scan_objects(s3)

	return sesitive_data

def main():

	####### Main starts here ####### 

	display_banner()

	#process arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--run', required=1)
	parser.add_argument('--config')
	parser.add_argument('--object')

	args = parser.parse_args()

	#load configurations
	if args.config == None:
		conf_file = "code/conf/cloud_dlp.conf"
	else:
		conf_file = args.config

	config = load_conf(conf_file)

	#aws_accounts = config['global_conf']['aws_accounts']
	#aws_role = config['global_conf']['aws_role']
	#dynamo_table = config['global_conf']['dynamo_table']
	#secret_regexs

	#Start logic
	if args.run == "full_scan":
		state = state_object.sensitive_data(config['global_conf']['dynamo_table'])
		scan_result = full_scan(config , state )
		print("Sensitive Data Found:")
		print(json.dumps(scan_result , sort_keys=True , indent=2))

	elif args.run == "scan_object":
		if args.object != None:
			#scan single object
			state = state_object.sensitive_data(config['global_conf']['dynamo_table'])
			scan_result = scan_single_object(config , state , args.object)
			print("Sensitive Data Found:")
			print(json.dumps(scan_result , sort_keys=True , indent=2))
		else:
			print("Please provide object_id")
			exit()

	elif args.run == "deploy_real_time_dlp":
		# Deploy Cloud formation template install realtime DLP
		print("Deploy Cloud formation template install realtime DLP")
	else:
	    print ("Usage: ")
	    print ("cloud_dlp.py --run scan_object --object <Json Object>")
	    print ("cloud_dlp.py --run full_scan")
	    

if sys.argv[0] != "/var/runtime/awslambda/bootstrap.py":
	main()

#sudo python3 code/cloud_dlp.py --run scan_object --object "{\"objects\" : [{\"object_id\" : \"523256993465:agentd2019:test_data.txt\", \"object_type\" : \"s3\",\"aws_account\": \"523256993465\",\"bucket\": \"agentd2019\", \"key\": \"test_data.txt\" }]}"