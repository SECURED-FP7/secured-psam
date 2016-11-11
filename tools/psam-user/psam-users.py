'''
@version: 1.0

PSAM-users Code
'''


import argparse
import json
from pprint import pprint
from upr_client import UPRClient
import os
import workflow_manager


UPR_URL=os.getenv('UPR_URL','http://195.235.93.146:8081')
PSAR_URL=os.getenv('PSAR_URL','http://195.235.93.146:8080')
SPM_URL=os.getenv('SPM_IP','10.95.211.17')


def get_user (args):
	try:
		c=UPRClient(UPR_URL)
		r=c.get_user_list()
		t=json.loads(r.text)

		with open(args.path, 'w') as outfile:
  			json.dump(t, outfile,sort_keys = True, indent = 4,ensure_ascii=False) 
		print "[INFO] The file was created."
	except:
		print "[ERROR]"
	return 0


def add_user (args):
	try:
		with open(args.path) as data_file:
			data = json.load(data_file)
		for i in range(0,len(data)):
			creator = "creator"
			try:
				creator=data[i]["creator"]
			except:
				pass
			if creator is not None:
				check=0
				for c in range(0,i):
					#print data[c]["user_id"]
					if creator==data[c]["user_id"]:				
						check=1
					else:
						pass
				if check==0:
					print "[ERROR] Please, orders the file."
					return 0
			
		for e in data:
			user_id=e["user_id"]
			c=UPRClient(UPR_URL)
			r=c.get_user_list(user_id=user_id)
			if r.status_code==404:
				try: 
					creator=e["creator"]
				except:
					pass
				try:
					optimization_profile=e["optimization_profile"]
				except:
					pass
				try:
					type=e["type"]
					is_admin=e["is_admin"]
					is_cooperative=e["is_cooperative"]
					is_infrastructure=e["is_infrastructure"]
					integrityLevel=e["integrityLevel"]	
				except:
					print "[ERROR] Invalid format"
	
				if creator != "" :
					r=c.create_user(user_id=user_id,password=user_id, integrityLevel=integrityLevel,type=type, is_cooperative=is_cooperative, is_infrastructure=is_infrastructure, is_admin=is_admin,creator=creator,optimization_profile=optimization_profile)
				else:
					r=c.create_user(user_id=user_id,password=user_id, integrityLevel=integrityLevel,type=type, is_cooperative=is_cooperative, is_infrastructure=is_infrastructure, is_admin=is_admin)
	
				if str(r)=="<Response [201]>":
					print "[INFO] The user " +user_id+ " was created."
				elif str(r)=="<Response [409]>":
					print "[ERROR] Conflict, the user " +user_id+ " already exists."
				else:
					pass
	except:
		print "[ERROR]"



	return 0




def delete_user(args):
	try:
		with open(args.path) as data_file:
        	        data = json.load(data_file)

		for e in data:
        	        user_id=e["user_id"]
			c=UPRClient(UPR_URL)
			r=c.delete_user(user_id=user_id)
			if str(r)=="<Response [204]>":
				print "[INFO] The user " +user_id+ " was removed."
			else:
				print "[ERROR] The user " +user_id+ "  could not be removed."
	except: 	
		print "[ERROR]"
	return 0

def get_hspl (args):
	try:
		c=UPRClient(UPR_URL)
		r=c.get_hspl()
		t=json.loads(r.text)

		with open(args.path, 'w') as outfile:
  			json.dump(t, outfile,sort_keys = True, indent = 4,ensure_ascii=False) 
		print "[INFO] The file was created."
	except:
		print "[ERROR]"
	return 0


def add_hspl (args):
	try:
		with open(args.path) as data_file:
			data = json.load(data_file)
		for e in data:
			editor=e["editor"]
			target=e["target"]
			hspl=e["hspl"]
			username=target

			c=UPRClient(UPR_URL)
			r=c.put_user_hspl(user_id=editor,hspl=hspl, target=target)
			if str(r)=="<Response [201]>":
				print "[INFO] The hspl was added from user " +editor
				try:
					wfm = workflow_manager.WorkflowManager(username, username, UPR_URL, SPM_URL, PSAR_URL)
					print "[INFO] WFM was running"				
				except:
					print "[ERROR] No WFM"

			elif str(r)=="<Response [409]>":
				print "[ERROR] Conflict"
			else:
				print "[ERROR]"
	except:
		print "[ERROR]"
	return 0

def callWarkflowManager(username):
        token = ""
        upr_url = UPR_URL
        #upr_url = upr_url.replace("http://", '')
        #upr_url = upr_url.split(":")[0]
        wfm = workflow_manager.WorkflowManager(username, token, upr_url, SPM_URL, PSAR_URL)




def delete_hspl(args):
	try:
		with open(args.path) as data_file:
        	        data = json.load(data_file)
		for e in data:
			c=UPRClient(UPR_URL)
        	        #user_id=e["editor"]
			try:
				hspl_id=e["id"]
				r=c.delete_hspl(user_id=user_id, hspl_id=hspl_id)
			except:
				print "[ERROR] Hspl_id not valid"
				#r=c.delete_hspl(user_id=user_id)
			if str(r)=="<Response [204]>":
				print "[INFO] The hspl " +hspl_id+ " was removed."
			else:
				print "[ERROR] The hspl " +hspl_id+ "  could not be removed."
	except: 	
		print "[ERROR]"
	return 0

def get_mspl (args):
	try:
		c=UPRClient(UPR_URL)
		r=c.get_mspl()
		t=json.loads(r.text)

		with open(args.path, 'w') as outfile:
  			json.dump(t, outfile,sort_keys = True, indent = 4,ensure_ascii=False) 
  			#json.dump(t, outfile) 
		print "[INFO] The file was created."
	except:
		print "[ERROR]"
	return 0


def add_mspl (args):
		#try:
		with open(args.path) as data_file:
			data = json.load(data_file)
		for e in data:
			target=e['target']
                	editor=e['editor']
                	capability=e['capability']
                	is_reconciled=e['is_reconciled']
                	mspl=e['mspl']

			c=UPRClient(UPR_URL)
			r=c.create_mspl(target=target,editor=editor,capability=capability,is_reconciled=is_reconciled, mspl=mspl)
			#print r		
			if str(r)=="<Response [201]>":
				print "[INFO] The mspl was created."
			elif str(r)=="<Response [409]>":
				print "[ERROR] Conflict "
			else:
				print "[ERROR]"
		#except:
		#print "[ERROR]"
		return 0




def delete_mspl(args):
		#try:
		with open(args.path) as data_file:
        	        data = json.load(data_file)
		#print data[0]

		for e in data:
			mspl_id=""
			target=""
			editor=""
			capability=""
			is_reconciled=""
			try:
				mspl_id=e["mspl_id"]
			except:
				pass
			try:
				editor=e["editor"]
			except:
				pass
			try:
				target=e["target"]
			except:
				pass
			try:
				capability=e["capability"]
			except:
				pass
			try:
				is_reconciled=e["is_reconciled"]			
			except:
				pass
			try:
				if mpsl_id!="":	
					c=UPRClient(UPR_URL)
					r=c.delete_mspl(mspl_id=mspl_id)
				else:
					c=UPRClient(UPR_URL)
					r=c.delete_mspl(target=target,editor=editor, capability=capability, is_reconciled=is_reconciled)
			except:
				print "[ERROR] Format not valid"
			#print user_id
			#print r
			if str(r)=="<Response [204]>":
				print "[INFO] Mspl deleted."
			else:
				print "[ERROR]"
		#except: 	
		#print "[ERROR]"
		return 0


def get_psa (args):
	try:
		c=UPRClient(UPR_URL)
		r=c.get_user_psa(args.user_id)
		t=json.loads(r.text)

		with open(args.path, 'w') as outfile:
  			json.dump(t, outfile,sort_keys = True, indent = 4,ensure_ascii=False) 

  			#json.dump(t, outfile) 
		print "[INFO] The file was created."
	except:
		print "[ERROR]"
	return 0


def add_psa (args):
	try:
		with open(args.path) as data_file:
			data = json.load(data_file)
		for e in data:
			user_id=args.user_id
			psa_id=e["psa_id"]
			active=e["active"]
			running_order=e["running_order"]
			c=UPRClient(UPR_URL)
			r=c.put_user_psa(user_id=user_id,psa_id=psa_id, active=active, running_order=running_order)
			#print r		
			if str(r)=="<Response [201]>":
				print "[INFO] The psa " +psa_id+ " was asociated from the user "+user_id
			elif str(r)=="<Response [409]>":
				print "[ERROR] Conflict, the user " +user_id+ " already has associated the "+psa_id
			else:
				print "[ERROR] The psa " +psa_id+ "  could not be associated from the user "+user_id
	except:
		print "[ERROR]"
	return 0




def delete_psa(args):
	try:
		with open(args.path) as data_file:
        	        data = json.load(data_file)
		#print data[0]

		for e in data:
        	        user_id=args.user_id
			try:
				psa_id=e["psa_id"]
			except:
				pass
			c=UPRClient(UPR_URL)
			try:
				r=c.delete_user_psa(user_id=user_id,psa_id=psa_id)
			except:
				r=c.delete_user_psa(user_id=user_id)
		
			#print user_id
			#print r
			if str(r)=="<Response [204]>":
				print "[INFO] The psa: "+psa_id+", from the user: "+user_id+"  was removed"
			else:
				print "[ERROR]"
	except: 	
		print "[ERROR]"
	return 0


def call_WFM (args):
        try:
                with open(args.path) as data_file:
                        data = json.load(data_file)
                for e in data:
                        username=args.user_id
			token=''
			upr_url=UPR_URL
                        SPM_URL=SPM_URL
			wfm = workflow_manager.WorkflowManager(username, token, upr_url, SPM_URL)


        except:
                print "[ERROR]"
        return 0



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
'''
Adding support for the commands required for the psam-users:
1.get_user
2.add_user
3.delete_user
4.get_hspl
5.add_hspl
6.delete_hspl
7.get_mspl
8.add_mspl
9.delete_mspl
10.get_psa
11.add_psa
12.delete_psa
13.call_WFM
'''

parser_get_user = subparsers.add_parser('get_user', description="Returns in standard output the list of users and their profiles. (JSON). If a file is included then store in the file")
parser_get_user.add_argument('path', type=str, help="A specific path in where is the project.")
parser_get_user.set_defaults(func=get_user)

parser_add_user= subparsers.add_parser('add_user', description="Provision of all users in the file")
parser_add_user.add_argument('path', type=str, help="The path of the file")
parser_add_user.set_defaults(func=add_user)

parser_delete_user= subparsers.add_parser('delete_user', description="Remove of all users in the file")
parser_delete_user.add_argument('path', type=str, help="The path of the file")
parser_delete_user.set_defaults(func=delete_user)

parser_get_hspl = subparsers.add_parser('get_hspl', description="Store in the file the list of hspl.")
parser_get_hspl.add_argument('path', type=str, help="The path of the file.")
parser_get_hspl.set_defaults(func=get_hspl)

parser_add_hspl= subparsers.add_parser('add_hspl', description="Provision of all hspl in the file")
parser_add_hspl.add_argument('path', type=str, help="The path of the file")
parser_add_hspl.set_defaults(func=add_hspl)

parser_delete_hspl= subparsers.add_parser('delete_hspl', description="Remove of all hspl in the file")
parser_delete_hspl.add_argument('path', type=str, help="The path of the file")
parser_delete_hspl.set_defaults(func=delete_hspl)


parser_get_mspl = subparsers.add_parser('get_mspl', description="Store in the file the list of mspl. ")
parser_get_mspl.add_argument('path', type=str, help="The path of the file.")
parser_get_mspl.set_defaults(func=get_mspl)

parser_add_mspl= subparsers.add_parser('add_mspl', description="Provision of all mspl in the file")
parser_add_mspl.add_argument('path', type=str, help="The path of the file")
parser_add_mspl.set_defaults(func=add_mspl)

parser_delete_mspl= subparsers.add_parser('delete_mspl', description="Remove of all mspl in the file")
parser_delete_mspl.add_argument('path', type=str, help="The path of the file")
parser_delete_mspl.set_defaults(func=delete_mspl)


parser_get_psa = subparsers.add_parser('get_psa', description="Store in the file the list of psas")
parser_get_psa.add_argument('path', type=str, help="The path of the file.")
parser_get_psa.add_argument('user_id', type=str, help="The name of the user.")
parser_get_psa.set_defaults(func=get_psa)

parser_add_psa= subparsers.add_parser('add_psa', description="Provision of all psas in the file for a specific user")
parser_add_psa.add_argument('path', type=str, help="The path of the file")
parser_add_psa.add_argument('user_id', type=str, help="The name of the user")
parser_add_psa.set_defaults(func=add_psa)

parser_delete_psa= subparsers.add_parser('delete_psa', description="Remove of all psas in the file")
parser_delete_psa.add_argument('path', type=str, help="The path of the file")
parser_delete_psa.add_argument('user_id', type=str, help="The name of the user.")
parser_delete_psa.set_defaults(func=delete_psa)

parser_call_WFM= subparsers.add_parser('call_WFM', description="Remove of all psas in the file")
parser_call_WFM.add_argument('path', type=str, help="The path of the file")
parser_call_WFM.set_defaults(func=call_WFM)


parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()
args.func(args)

