# -*- coding: utf-8 -*-
#from django.shortcuts import render
from rest_framework import status
from PSAM_status import *
from rest_framework.response import Response
from rest_framework.views import APIView
from models import PSA
from serializers import PSASerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
import json, os
from ConfigParser import SafeConfigParser
import os, logging, json
from requests import post, get, put, delete
import hashlib
from client_psar import Client
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('psam.conf')
logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))
PSAR_URL=parser.get('PSAR','psar_ip')
print PSAR_URL

#class PsamPublicationsView(APIView):
class PsamView(APIView):

	def put(self,request,psa_id):
		"""
		Publish PSA

		token -- (NOT required)

		"""
		psa=""
		try:
			psa=PSA.objects.get(psa_id=psa_id)
		except:
			print "Psa don't exist"
		pathFileZip=psa_id+'.zip'
		pathFile=psa_id
		data={}
		data['manifest']=""
		data['plugin']=""
		data['image']=""
		data['info_manifest']=""
		data['info_plugin']=""
		data['info_image']=""
		data['info']=""
		data['dyn_conf']=""
		data['info_dyn_conf']=""
		#Step 1. retrieve the packed(zipped project file) from the developer
		#logging.info("Receiving ZIP for PSA %s", psa_id)
		try:
			with open (psa_id+'.zip', 'wb+')as f:
				for chunk in request.data['file'].chunks():
					f.write(chunk)
				print 'Info, saved the file'
		except: 
			print 'Error, no saved the file'
		#Step 2. unzip the project and check that all files are present and 
		#maybe re-validate the project similar to what the psam-project tool does.
		from zipfile import ZipFile
		try:
			with ZipFile(pathFileZip) as myzip:
				myzip.extractall(pathFile)
				print 'Unzip the project '+ pathFileZip
			os.remove(pathFileZip)
		except:
			print("Error, no unziped the project")
			return Response(status=status.HTTP_400_BAD_REQUEST)			

		#logging.info("Validating project %s", psa_id)
		print 'Validating project '+psa_id
		plugin = ""
		manifest = ""
		mspl = ""
		image= ""
		dyn_conf=""
		files=os.listdir(pathFile)
		check_plugin=False
		check_manifest=False
		check_image=False
		check_mspl=False
		check_dyn_conf=False
		checkOneFileExists=False

		for e in files:
			if e.find('_manifest.xml')>0:
				check_manifest=True
				manifest=e
				manifestHash=gethash(psa_id+'/'+manifest)
				checkOneFileExists=True
			if e.find('_mspl.xml')>0:
				check_mspl=True
				mspl=e
				msplHash=gethash(psa_id+'/'+mspl)	
				checkOneFileExists=True
			if e.find('plugin.jar')>0:
				check_plugin=True
				plugin=e
				pluginHash=gethash(psa_id+'/'+plugin)	
				checkOneFileExists=True
			#formats image: qcow2, raw, vhd, vmdk, vdi, iso, aki, ari or ami
			if e=='dyn_conf.txt':
				check_dyn_conf=True
				dyn_conf=e
				checkOneFileExists=True
			if e.find('.qcow2')>0:
				format="qcow2"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.raw')>0:
				format="raw"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.vhd')>0:
				format="vhd"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.vmdk')>0:
				format="vmdk"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.vdi')>0:
				format="vdi"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.iso')>0:
				format="iso"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.aki')>0:
				format="aki"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.ari')>0:
				format="ari"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True
			if e.find('.ami')>0:
				format="ami"
				check_image=True
				image=e
				imageHash=gethash(psa_id+'/'+image)
				checkOneFileExists=True

		if checkOneFileExists==False:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		if (check_plugin==True and check_mspl==True):
			r=isPluginValid(psa_id=psa_id, plugin=plugin, mspl=mspl)
			if str(r)=="True":
				data['plugin']="[INFO] M2LPlugin validation: SUCESS"
			elif str(r)=="False":
				data['plugin']="[ERROR] M2LPlugin validation: ERROR"
				return Response(status=status.HTTP_400_BAD_REQUEST, data=data)				
		#else:
		#	return Response (status=status.HTTP_400_BAD_REQUEST)

		if (check_manifest==True and check_image==True):
			imageNameManifestImageCrossCheck(psa_id=psa_id,manifest=manifest, image=image)
			r=validateManifest(psa_id=psa_id, manifest=manifest)
			if str(r)=="True":
				data['manifest']="[INFO] Manifest validation: SUCESS"
			elif str(r)=="False":
				data['manifest']="[ERROR] Manifest validation: ERROR"
				logging.info('%s %s: 400 BAD_REQUEST',request.method,'/v1/psam/images/')
				return Response(status=status.HTTP_400_BAD_REQUEST, data=data)				

		else:
			logging.info('%s %s: 400 BAD_REQUEST',request.method,'/v1/psam/images/')
			return Response (status=status.HTTP_400_BAD_REQUEST)

		#Create a hash of the files if is the first time. And save it in the BBDD

		#Check the hash and only if is diferent continue
		if psa=="":
			psa=PSA(psa_id=psa_id,hash_manifest=" ",hash_plugin=" ",hash_mspl=" ",hash_image=" ")
			psa.save()
			client=Client(PSAR_URL)
			r=client.create_psa(id=psa_id, name=psa_id, plugin_id=psa_id, manifest_id=psa_id)
			if str(r)=="<Response [200]>":
				data['info']="[INFO] Created new PSA on PSAR"
			if str(r)=="<Response [201]>":
				data['info']="[INFO] Created new PSA on PSAR"
			if str(r)=="<Response [401]>":
				data['info']= "[INFO] Post PSA 401 UNAUTHORIZE" 
			if str(r)=="<Response [409]>":
				data['info']="Please before publishing this project, do: python psam-onboard.py list"
		if (psa.hash_manifest!=manifestHash):
			client=Client(PSAR_URL)
			r=client.put_manifest_file(psa_id,psa_id+'/'+manifest)
			if str(r)=="<Response [200]>":
				psa.hash_manifest=manifestHash
				data['info_manifest']="[INFO] Manifest published on the PSAR"

			if str(r)=="<Response [401]>":
				data['info_manifest']="[ERROR] Put manifest 401 UNAUTHORIZED"
			if str(r)=="<Response [404]>":
				data['info_manifest']="[ERROR] NOT FOUND PSA IN PSAR"

		if (psa.hash_image!=imageHash):
			client=Client(PSAR_URL)
			r=client.put_image_file(psa_id,psa_id+'/'+image,format,'bare')
			if str(r)=="<Response [200]>":
				psa.hash_image=imageHash
				data['info_image']="[INFO] Image published on the PSAR"
			if str(r)=="<Response [401]>":
				data['info_image']="[ERROR] Put image 401 UNAUTHORIZED"
			if str(r)=="<Response [400]>":
				data['info_image']="[ERROR] Put image 400 BAD REQUEST"
			if str(r)=="<Response [404]>":
				data['info_image']="[ERROR] NOT FOUND PSA IN PSAR"
		if(check_dyn_conf==True):
			import json
			client=Client(PSAR_URL)
			try:
				with open(psa_id+'/dyn_conf.txt') as data_file:
					dataJson=json.load(data_file)
				for e in dataJson:
					location=e["location"]
					dynamic_conf=e["dyn_conf"]
					r=client.put_dyn_conf(psa_id=psa_id,location=location,dyn_conf=dynamic_conf)
					if str(r)=="<Response [200]>":
						data['info_dyn_conf']="[INFO] Dynamic configuration saved"
					if str(r)=="<Response [201]>":
						data['info_dyn_conf']="[INFO] Dynamic configuration saved"
                        		if str(r)=="<Response [400]>":
                                		data['info_dyn_conf']="[ERROR] Put dynamic configuration 400 BAD REQUEST"
                        		if str(r)=="<Response [404]>":
                                		data['info_dyn_conf']="[ERROR] NOT FOUND PSA IN PSAR"
					if (str(r)!="<Response [404]>") and(str(r)!="<Response [400]>") and (str(r)!="<Response [201]>") and (str(r)!="<Response [200]>"):
						data['info_dyn_conf']="[ERROR] Dynamic configuration not saved"

			except:
				data['info_dyn_conf']="[ERROR] Dynamic configuration not saved"
				print 'No dynamic config'
		
		if (psa.hash_plugin!=pluginHash):
			client=Client(PSAR_URL)
			r=client.put_plugin_file(psa_id,psa_id+'/'+manifest)
			if str(r)=="<Response [200]>":
				psa.hash_plugin=pluginHash
				data['info_plugin']="[INFO] Plugin published on the PSAR"
			if str(r)=="<Response [401]>":
				data['info_plugin']="[ERROR] Put plugin 401 UNAUTHORIZED"
			if str(r)=="<Response [404]>":
				data['info_plugin']="[ERROR] NOT FOUND PSA IN PSAR"

		if (psa.hash_mspl!=msplHash):
			psa.hash_mspl=msplHash
		psa.save()
		#Step 3. create the PSA project in PSAR and then push all the project files : 

		##	PSAR API registering: POST /v1/PSA/image/

		##	PSAR API image upload

		##	PSAR API manifest upload

		##	PSAR API plugin upload

		#Step 4: Delete the project files locally from PSAM
		#os.removedirs(pathFile)
		import shutil
		shutil.rmtree(pathFile)
		logging.info('%s %s: 200 OK',request.method,'/v1/psam/images/')

		return Response(status=status.HTTP_200_OK, data=data)	



	def delete(self,request, psa_id):
		"""
		Remove PSA and all the dependecies 

		token -- (NOT required)
		"""
		try:
			psa=PSA.objects.get(psa_id=psa_id)
			psa.delete()
			client = Client(PSAR_URL)
			r=client.delete_psa(psa_id)
			if str(r)=="<Response [204]>":
				logging.info('%s %s: 204 NO_CONTENT',request.method,'/v1/psam/images/')
                		return Response(status=status.HTTP_204_NO_CONTENT)
			elif str(r)=="<Response [404]>":
				logging.info('%s %s: 404 NOT_FOUND',request.method,'/v1/psam/images/')
				return Response(status=status.HTTP_404_NOT_FOUND)
			elif str(r)=="<Response [401]>":
				logging.info('%s %s: 401 UNAUTHORIZE',request.method,'/v1/psam/images/')
				return Response(status=status.HTTP_401_UNAUTHORIZE) 
		except:
			client = Client(PSAR_URL)
			r=client.delete_psa(psa_id)
			if str(r)=="<Response [204]>":
				logging.info('%s %s: 204 NO_CONTENT',request.method,'/v1/psam/images/')
                		return Response(status=status.HTTP_204_NO_CONTENT)
			elif str(r)=="<Response [404]>":
				logging.info('%s %s: 404 NOT_FOUND',request.method,'/v1/psam/images/')
				return Response(status=status.HTTP_404_NOT_FOUND)
			elif str(r)=="<Response [401]>":
				logging.info('%s %s: 401 UNAUTHORIZE',request.method,'/v1/psam/images/')
				return Response(status=status.HTTP_401_UNAUTHORIZE) 




class PsamImages(APIView):
	"""
	"""
	def get(self, request):
		"""
		Shows a list of all existing PSAs. Accepts parameter 'psa_id' and, if it exists, shows only matching PSAs

		token -- (NOT required)
		psa_id -- (NOT required)

		"""
		client = Client(PSAR_URL)
		if 'psa_id' in request.query_params:
			psa_id= request.query_params['psa_id']
			r=client.get_image_list(psa_id)
		else:
			r=client.get_image_list()
		if str(r)=="<Response [200]>":
			data=json.loads(r.text)
			for e in data:
				#print e['psa_id']
				#print e['psa_image_hash']
				try:
					psa=PSA.objects.get(psa_id=psa_id)
					psa.hash_image=str(e['psa_image_hash'])
					psa.save()
				except:
					psa=PSA(psa_id=str(e['psa_id']), hash_image=str(e['psa_image_hash']))
					psa.save()
			objects=PSA.objects.all()
			if 'psa_id' in request.query_params:
				objects=objects.filter(psa_id=request.query_params['psa_id'])
			logging.info('%s %s: 200 OK',request.method,'/v1/psam/images/')
	        	return Response(status=status.HTTP_200_OK, data=data)
		elif str(r)=="<Response [404]>":
			logging.info('%s %s: 404 NOT_FOUND',request.method,'/v1/psam/images/')
			return Response(status=status.HTTP_404_NOT_FOUND)
		elif str(r)=="<Response [401]>":
			logging.info('%s %s: 401 UNAUTHORIZE',request.method,'/v1/psam/images/')
			return Response(status=status.HTTP_401_UNAUTHORIZE)
		elif str(r)=="<Response [400]>":
			logging.info('%s %s: 400 BAD_REQUEST',request.method,'/v1/psam/images/')
			return Response(status=status.HTTP_400_BAD_REQUEST)









class v1Status(APIView):
        """
        Dummy. If the server is up, returns HTTP code 200
        """
        def get(self,request):
		logging.info('%s %s: 200 OK',request.method,'/v1/psam/status/')
                return Response(status=status.HTTP_200_OK)






def gethash (file):
	hash_func=hashlib.new('sha256')
        with open(file,'rb') as f:
                f.seek(0,os.SEEK_END)
                size=f.tell()
        i=0
        with open(file,'rb') as f:
                while i<size:
                        hash_func.update(f.read(512))
                        i+=512
        return hash_func.hexdigest()





def isPluginValid (psa_id, plugin, mspl):

	print "Validating plugin " +str(plugin)
	tester = '../../Utilities/M2LPluginTester.jar'
	pluginpath = psa_id+'/'+plugin
    	msplpath = psa_id+'/'+mspl
	path=os.getcwd()
	#print path
    	tempconf = '../../Utilities/tempconf'
    	command = 'java -jar  '+tester+' .'+plugin+' .'+mspl+' '+tempconf
    	try:
        	from subprocess import STDOUT,Popen,PIPE 
		out,err = Popen(command, cwd=path, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()

		if err is not None:
		    		print '[ERROR] M2lPlugin validation: FAIL'
            			print err
		if 'Exception' in out or 'exception' in out:
		    		print '[ERROR] M2lPlugin validation: FAIL'
            			print out
				return False
		if err is None:
				print '[INFO] M2lPlugin validation: DONE' 
	except Exception as e:
       		print False
      		print '[ERROR] M2lPlugin validation: FAIL'
	return True


def imageNameManifestImageCrossCheck (psa_id, manifest, image):
	manifest = psa_id+'/'+manifest
        manifestImageName = None
	manifestImageFormat = None
        imageName = image.split('/')[-1]
	try:
        	from xml.dom import minidom
            	doc = minidom.parse(manifest)
            	node= doc.getElementsByTagName("general_info")[0]
            	manifestImageName = node.getElementsByTagName("name")[0].firstChild.data

		node= doc.getElementsByTagName("configuration")[0]
            	manifestImageFormat = node.getElementsByTagName("PSA_format")[0].firstChild.data
        except Exception as e:
        	print e
		print '[ERROR] Image and Manifest cross validation: FAIL'
	        print '[ERROR] Cannot process manifest file.'
	if manifestImageFormat is None :
	       	print '[ERROR] Image and Manifest cross validation: FAIL'
	       	print '[ERROR] Could not identify PSA Image format from manifest.'
	elif manifestImageName is None:
            	print '[ERROR] Image and Manifest cross validation: FAIL'
            	print '[ERROR] Could not identify PSA Image name from manifest.'
	if imageName == (manifestImageName+'.'+manifestImageFormat):
		print '[INFO] Validation Name of Image DONE'
	else:
        	print '[ERROR] Image and Manifest cross validation: FAIL'
            	print '[ERROR] Image Name and Manifest reference are different.'
        	print '[ERROR] Image Name:',imageName
      		print '[ERROR] Image Name in Manifest:',(manifestImageName+'.'+manifestImageFormat)

	return 0





"""
This method validates the xml manifest file using the PSA Manifest xsd schema.
"""
def validateManifest(psa_id, manifest):
        #Getting the manifest file's path to read its contents
        manifest = psa_id+'/'+manifest
	path=os.getcwd()
        try:
            from lxml import etree
        except:
            print '[ERROR] Manifest Format Validation: FAIL'
            print '[ERROR] lxml module is needed to validate the manifest file.\n Please install lxml: pip install lxml'
            return False
        
        def validate(xmlparser, xmlfilename):
            try:
                with open(xmlfilename, 'r') as f:
                    etree.fromstring(f.read(), xmlparser) 
                return True
            except Exception as e:
                print e
                print '[ERROR] Manifest Format Validation: FAIL'
                print '[ERROR] Could not read manifest file correctly.'
                return False
        #Creating an xml parser based on the PSAManifest schema
        try:
            with open(path+'/Utilities/PSA_manifest.xsd', 'r') as f:
                schema_root = etree.XML(f.read())
            
            schema = etree.XMLSchema(schema_root)
            xmlparser = etree.XMLParser(schema=schema)
        except Exception as e:
            print '[ERROR] Manifest Format Validation: FAIL'
            print '[ERROR] Could not read manifest schema in Utilities/PSA_manifest.xsd correctly.'
            print e
            return False
        
        #Validating the PSAManifest xml file using the xmlparser
        if validate(xmlparser, manifest):
            return True
        else:
            return False
    
"""    
**********LEGACY FUNCTION USING JSON MANIFEST**********
Manifest format validation when manifest file was JSON.
"""
def isManifestFormatValid(psa_id, manifest):
        import json
        #Getting the manifest file's path to read its contents
        manifest = psa_id+'/'+manifest
        
        #1. Validating Manifest general json schema
        
        try:
            f = open(manifest,'r')
            data = f.read()
            f.close()
            manifestObject = json.loads(data)
        except Exception as e:
            print e
            print type(e)
            print e.args
            print '[ERROR] Manifest is not a valid json file.'
            return False
        
        """
        2. Validating that Manifest contains the correct fields as follows:
        {
            "PSA_id":"",
            "disk": "",
            "interface": [
                    {
                    "network":"data", 
                    "type":"data_in"
                    },
                    {
                    "network":"data", 
                    "type":"data_out"
                    },
                    {
                    "network":"control", 
                    "type":"manage"
                    }
                ],
            "memory": "",
            "IP":"",
            "os-architecture": "",
            "vcpu": ""
        }
        """ 
        #Mandatory parameters inside a manifest file. 
        #We use it ot validate that these and only these parameters are present in the manifest file.
        manifestKeys = ["PSA_id","disk","interface","memory","IP","os-architecture","vcpu"]
        psaInterfaces = sorted([
                    {
                     "network":"data", 
                     "type":"data_in"
                    },
                    {
                     "network":"data", 
                     "type":"data_out"
                    },
                    {
                     "network":"control", 
                     "type":"manage"
                    }
                ])
        #Checking if the number of the manifest parameters is correct
        if len(manifestObject) != len(manifestKeys):
            print '[ERROR] Manifest Format Validation: FAIL'
            print '[ERROR] The number of valid parameters for the manifest is:'+str(len(manifestKeys))
            return False
        
        #Checking that the manifest parameters are valid parameters i.e. are part of the correct set of parameters
        for key in manifestObject:
            if key not in manifestKeys:
                print '[ERROR] Manifest Format Validation: FAIL'
                print '[ERROR] '+key+' is not a valid manifest parameter.'
                return False
        
        #Checking that all manifest parameters are present in the the project's manifest
        for key in manifestKeys:
            if key not in manifestObject:
                print '[ERROR] Manifest Format Validation: FAIL'
                print '[ERROR] '+key+' does not exist.'
                return False
        
        '''
        Manifest Interfaces Validation:
        -------------------------------
        Step 1. Firstly we check that the manifest has the correct number of interfaces specified.
        Step 2. Secondly we check that each interface has two parameters
        Step 3. Finally we check that the interface parameters and values are correct
        '''
        manifestInterfaces = sorted(list(manifestObject['interface']))
        
        #Step 1.
        if len(manifestInterfaces) != len(psaInterfaces):
            print '[ERROR] Manifest Format Validation: FAIL'
            print '[ERROR] The number of interfaces must be:'+str(len(psaInterfaces))
            return False 
        
        #Step 2.
        for iface in manifestInterfaces:
            if len(iface) != 2:
                print '[ERROR] Manifest Format Validation: FAIL'
                print '[ERROR] Wrong Interface:'
                print iface
                print '[ERROR] An interface must have only 2 parameters:{network, type}'
                return False 
        
        #Step 3.
        for interface_pair in zip(sorted(psaInterfaces), sorted(manifestInterfaces)):
            for (correct_iface_key,correct_iface_value),(manifest_iface_key,manifest_iface_value) in zip(interface_pair[0].items(), interface_pair[1].items()):
                if correct_iface_key != manifest_iface_key:
                    print '[ERROR] Manifest Format Validation: FAIL'
                    print '[ERROR] '+manifest_iface_key+' not a valid interface parameter.'
                    return False
                if correct_iface_value != manifest_iface_value:
                    print '[ERROR] Manifest Format Validation: FAIL'
                    print '[ERROR] '+manifest_iface_value+' is not a valid value for interface parameter:'+correct_iface_key
                    return False
                        
        return True
                
        
'''
**********LEGACY FUNCTION USING JSON MANIFEST**********
Checks whether the PSA image is the one referenced by the PSA Manifest.
'''


