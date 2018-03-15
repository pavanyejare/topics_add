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
#Change the title for videos 
#Plase give .csv file as argument
#script shuld be run only python 2 or 2.7 version
#	 Example -
#                python2  test.py  FILE_NAME.csv
#
#   ----------------------------  CSV FILE   ------------------------------------------
#   -     IN csv file g_conf_id and Title should be speredte by ;(semicolon)         -
#   -     Example of cvs file -      						      -
#   -             g_conf_id;VIDEO TITLE	   	 				      -
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


CLIENT_ID="cibacd4c6fe19e4023abea0e64991c360b"
SECRET_KEY="sk891dc6ee5fd14a0fbb13ddfb7084be01"
DOMAIN_NAME="ktpl.kpoint.com"
EMAIL="ksupport@kpoint.com"
DISPLAYNAME="Site Administrator"

def initLogger() :
    log_file =  "title_status.log"
    #Clearing the file if already present
    open(log_file, 'w').close()
    logging.basicConfig(filename=log_file,level=logging.INFO,format='%(asctime)s %(levelname)s - %(message)s')

def write_faild(gconfid,title):
	with open('faild_gconfid.log', 'a') as csvfile:
		fieldnames = ['g_cong_id', 'title']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
		writer.writerow({'g_cong_id': gconfid, 'title': title})


def generate_xauth_token(email, displayname):
	challenge = str(int(time.time()))
	xauth_message = CLIENT_ID + ":" + email + ":" + displayname + ":" + challenge
	hmacToken = hmac.new(str(SECRET_KEY), str(xauth_message))
	xauth_token=base64.urlsafe_b64encode(hmacToken.digest()).replace("=","")
	xtencode= "client_id="+ CLIENT_ID +"&user_email="+ email +"&user_name="+ displayname +"&challenge="+challenge+"&xauth_token="+xauth_token;
	xt=base64.urlsafe_b64encode(xtencode).replace("=","")
	return xt

def login(gconfid,title):
	xttoken = generate_xauth_token(EMAIL, DISPLAYNAME)
	url = "https://"+ DOMAIN_NAME +"/api/v1/xapi/kapsule/"+gconfid
	url = url + "?xt=" + xttoken 
	data=requests.get(url)
	update=requests.put(url,data={'title': title })
	#### status code in not equal to 200  ###
	if (update.status_code != 200 ):
		error=update.json().get('error')
		write_faild(gconfid,title)
		print ("Error: Update title faild -"+error)
		logging.error("Update title faild - "+ gconfid +":"+error)		

	else :
		print "Success: "+gconfid+"\tChnaged title"
		logging.info("Success : Changed title for "+ gconfid)
def man():
	print ("--------------- Help Page -----------------\n")
	print ("Plase give .csv file as argument ")
	print ("script shuld be run only python 2 or 2.7 version ")
	print "	Example -\n\t\tpython2 ",sys.argv[0] ," FILE_NAME.csv"
	print ("CSV FILE - ")
	print ("\tIN csv file g_conf_id and title should be speredte by ;(semicolon) ")
	print ("\tExample of cvs file - \n\t\tgcc-f1dbff42-c98f-4b82-8205-32624b5b18a4;VIDEO TITLE\n")
	print ("--------------- Help Page -----------------")
	
def read_csv():
	try:
		f_name = sys.argv[1]	
		open_file = open(f_name)
		csv_file = csv.reader(open_file, delimiter=";")
		count =  1
		for i in csv_file:
			gconfid = i[0] 
			title = i[1]
			login(gconfid,title)
	except Exception as e:
		print "-------------  CSV File Error :", e , "-------------"
		logging.error("CSV ERROR : "+ e)
		print("Please check csv file : \n 1. It should be filed speredte by ;(semicolon)")
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

