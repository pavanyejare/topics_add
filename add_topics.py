#!/usr/bin/python
import time, hmac, base64
import requests
import json
import subprocess
import sys
import os
import csv
import logging

##########################################################################################
#Change the topics for videos 
#Plase give .csv file as argument
#script shuld be run only python 2 or 2.7 version
#	 Example -
#                python2  test.py  FILE_NAME.csv
#
#   ----------------------------  CSV FILE   ------------------------------------------
#   -     IN csv file g_conf_id and topics should be speredte by ;(semicolon)         -
#   -     Multiple topics should be seprated by ,(comma)                              -
#   -     Example of cvs file -      						      -
#   -             g_conf_id;topics1,topics2,topics3 				      -
#   -     NOTE - Topics name should be more than 3 character                          -
#   -----------------------------------------------------------------------------------
#
#
#IMP : Change the  CLIENT_ID=""
#		   SECRET_KEY=""
#                  DOMAIN_NAME=""
#                  EMAIL="" 
#                  DISPLAYNAME="" 
#       as per your domain requirment 
###########################################################################################


CLIENT_ID=""
SECRET_KEY=""
DOMAIN_NAME=""
EMAIL=""
DISPLAYNAME=""

def initLogger() :
    log_file =  "topics_status.log"
    #Clearing the file if already present
    open(log_file, 'w').close()
    logging.basicConfig(filename=log_file,level=logging.INFO,format='%(asctime)s %(levelname)s - %(message)s')

def write_faild(gconfid,topics):
	with open('faild_gconfid.log', 'a') as csvfile:
		fieldnames = ['g_cong_id', 'Topics']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
		writer.writerow({'g_cong_id': gconfid, 'Topics': topics})


def generate_xauth_token(email, displayname):
	challenge = str(int(time.time()))
	xauth_message = CLIENT_ID + ":" + email + ":" + displayname + ":" + challenge
	hmacToken = hmac.new(str(SECRET_KEY), str(xauth_message))
	xauth_token=base64.urlsafe_b64encode(hmacToken.digest()).replace("=","")
	xtencode= "client_id="+ CLIENT_ID +"&user_email="+ email +"&user_name="+ displayname +"&challenge="+challenge+"&xauth_token="+xauth_token;
	xt=base64.urlsafe_b64encode(xtencode).replace("=","")
	return xt

def login(gconfid,topics):
	xttoken = generate_xauth_token(EMAIL, DISPLAYNAME)
	url = "https://"+ DOMAIN_NAME +"/api/v1/xapi/kapsule/"+gconfid
	url = url + "?xt=" + xttoken 
	data=requests.get(url)
	old_data=data.json().get('tags')
	old_data = ','.join(map(str, old_data))
	new_topic = old_data + "," + topics
	update=requests.put(url,data={'topics': new_topic })
	# status code in not equal to 200 
	if (update.status_code != 200 ):
		error=update.json().get('error')
		write_faild(gconfid,topics)
		print ("Error: Update topics faild -"+error)
		logging.error("Update topics faild - "+ gconfid +":"+error)		

	else :
		print "Success: "+gconfid+"\tAdded topics for"
		logging.info("Success : Added topics for "+ gconfid)
def man():
	print ("--------------- Help Page -----------------\n")
	print ("Plase give .csv file as argument ")
	print ("script shuld be run only python 2 or 2.7 version ")
	print "	Example -\n\t\tpython2 ",sys.argv[0] ," FILE_NAME.csv"
	print ("CSV FILE - ")
	print ("\tIN csv file g_conf_id and topics should be speredte by ;(semicolon) \n	Multiple topics should be seprated by ,(comma)")
	print ("\tExample of cvs file - \n\t\tgcc-f1dbff42-c98f-4b82-8205-32624b5b18a4;Video_Song,java,javascript,html,world_wide_web\n")
	print ("--------------- Help Page -----------------")
	
def read_csv():
	try:
		f_name = sys.argv[1]	
		open_file = open(f_name)
		csv_file = csv.reader(open_file, delimiter=";")
		count =  1
		for i in csv_file:
			gconfid = i[0] 
			topics = i[1]
			flag=0
			check_topic=topics.split(",")
			for t in range(len(check_topic)):
				if (len(check_topic[t])<=3):
					flag=1
					break
			if (flag == 1):
				print ("Error: "+gconfid+"\t\tTopics size is less than 3 character")
				logging.error("Topics size is less than 3 character "+ gconfid)
				write_faild(gconfid,topics)
				continue
			login(gconfid,topics)
	except Exception as e:
		print "-------------  CSV File Error :", e , "-------------"
		logging.error("CSV ERROR : "+ e)
		print("Please check csv file : \n 1. It should be filed speredte by ;(semicolon) \n 2. Topics seprated by ,(comma)")
		print("Please see help page")
		print "\tpython2 ",sys.argv[0] ," --help or -h"
		print "-------------  CSV File Error -------------"
def main():
	if len(sys.argv) <= 1:
		man()
	elif (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
		man()
	else:
		read_csv()
		print ("\n** Please check faild_gconfid.log file in you current directory to find out faild gconfid ** \n")
initLogger()
main()

