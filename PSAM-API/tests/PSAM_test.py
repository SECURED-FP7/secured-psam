from requests import get, put, post, delete
import os

PSAM_URL= os.getenv('PSAM_URL','http://10.95.211.18:8083')
base_url=PSAM_URL+'/v1/psam/'
test_project_name="test_psa"
path="test_psa.zip"


def test_create_psas():
	url=base_url+'images/'+test_project_name+'/'
	params={}
	with open(path, 'rb') as f:
		files={'file':f}	
		r=put(url,files=files, params=params)
		assert r.status_code==200
	
def test_list_psa():
	url=base_url+'images/'
	params={}
	params['psa_id']=test_project_name
	r=get(url,params=params)
	assert r.status_code==200

def test_delete_psa():
	url=base_url+'images/'+test_project_name+'/'
	params={}
	r=delete(url, params=params)
	assert r.status_code==204	
	r=delete(url, params=params)
	assert r.status_code==404	
