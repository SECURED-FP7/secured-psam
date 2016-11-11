'''
@note: created on 14/06/2016
@version: 1.0

PSAM-Onboard Code
-----------------
This tool offer a cli script to on-board and manage status of a PSA in the PSAM.
'''
import shutil
import argparse
import sqlite3, os, sys, json
from requests import get, put, delete, patch, post

PSAM_URL= os.getenv('PSAM_URL','http://195.235.93.146:8083')
base_url=PSAM_URL+'/v1/psam/'
token=None
tableName = 'psam_onboard'
tool_path_dir = os.path.realpath(__file__).split('psam-onboard.py')[0]
dbName = tool_path_dir+'Utilities/PSAM_ONBOARD.db'

'''
=====================================================
/////////////////////////////////////////////////////
Utility Functions:
////////////////////////////////////////////////////
====================================================
'''

'''
Connecting to the tool's database. The tool uses an sqlite database to store projects' paths.
if this is the first time the tool is used we create the projects' table. 
'''
def initializeDB():
    global tableName, dbName

    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    sql = 'create table if not exists ' + tableName + ' (id INTEGER PRIMARY KEY, project varchar(50) UNIQUE, path varchar(100))'
    c.execute(sql)
    conn.commit()
    c.close()
    conn.close()

'''
Creates a new a db connection and returns the connector instance.
'''
def connectDB():
    global tableName, dbName
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    return (conn,c)
    
'''
Adding a new project to the database:
for each project we store its path on the local system.
'''    
def addProject(connections, projectName, path):
    global tableName
    conn, c = connections
    c.execute('insert into ' + tableName + '(project,path) values (?, ? )',(projectName, path))
    conn.commit()
    c.close()
    conn.close()

'''
Removes the database entry for the deleted project
'''
def deleteProject(projectName):
    global tableName
    connections = connectDB()
    conn, c = connections
    c.execute('delete from ' + tableName + ' where project=?',(projectName,))
    conn.commit()
    c.close()
    conn.close()
    
'''
Retrieves the path for the given project.
'''
def getProjectPath(projectName):
    global tableName
    print '[INFO] Getting path for:'+args.project_name
    initializeDB()
    connections = connectDB()
    conn, c = connections
    
    c.execute('select path from ' + tableName + ' where project=?',(projectName,))
    
    row = c.fetchone()
    conn.commit()
    c.close()
    conn.close()
    if row is None:
        return None
    else:
        return row[0]
    
'''
Checks whether the given path exists on the local file system.
'''        
def validatePath(path):
    try:
	r= os.path.exists(path)
    	return r
    except:
	r=os.path.isfile(path)
        return r
'''
Deletes the given directory with all its contents.
'''
def removeDirectory(path):
    try:
    	import shutil
   	shutil.rmtree(path)
    except:
	os.remove(path)
    
'''
Removes all files in the given path that end with given suffix.
It is used by add-manifest, add-image and add-plugin to remove previously added
manifest, image or plugin respectively.
'''    
def removeFileBySuffix(suffixes, path):
        from os import listdir,remove
        from os.path import isfile, join

        to_remove = []
        for f in listdir(path):
            if isfile(join(path, f)):
                project_file = join(path, f)
                for suffix in suffixes:
                    if project_file.endswith(suffix):
                        to_remove.append(project_file)
        for f in to_remove:
            remove(f)
                    
                

'''
=====================================================
/////////////////////////////////////////////////////
Core functions Implementation Code:
////////////////////////////////////////////////////
====================================================
'''

def init(args):
    print '[INFO] Initialize project:'+args.project_name
    path = args.path
    if path is None:
    	print '[INFO] Enter a valid path'
    	return 0
    """
    if validatePath(path):
        if not validatePath(path+'/'+args.project_name):
            print '[ERROR] Project already exists.'
            return 0
    """

    try:
	s=path.split('/')
	l= len(s)
	i=0;
	path1=""
	for i in range(0, l-1):
		path1=path1+s[i]+'/'
	r=s[l-1].split('.')
	rl= len(r)
	if len(r)==1:
		directory=r[0]
		ext = r[0]
	else:
		directory=r[0]
		ext = r[1]
	if ext=="zip":
		if not os.path.isfile(path):
       			print '[ERROR] Project already exists.'
       			return 0

		#shutil.move(path1+'/'+directory, path1+'/'+args.project_name+'/'+args.project_name+'.zip')		
       		#print '[INFO] Creating project at:'+path+'/'+args.project_name
       		#os.mkdir(path+'/'+args.project_name)
       		#print "[INFO] Created the project at:"+path+'/'+args.project_name
	else:
		try:
		        import shutil
			zipFileName=r[0]
	 		shutil.make_archive(zipFileName, 'zip', path)
       			#shutil.move(zipFileName+'.zip', path)
			path=path+'.zip'
			print path
		except Exception as e:
       			print e
       			print '[ERROR] Could not pack project. Exiting.'
       			return 0

    except Exception as e:
       print e
       print '[ERROR] Project could not be created.'
       return 0





    try:
       initializeDB()
       connections = connectDB()
       addProject(connections, args.project_name, path)
    except Exception as e:
       print e
       print '[ERROR] Could register project to the database. Removing project directory'
       if (removeDirectory(path)):
                print '[INFO] Cleared project data.'
       else:
                print '[ERROR] Could not remove project files and folders. Please remove manually the project directory and data.'
       return 0


def list(args):
    """
    API methods called: PSAM PSA list API
    Check if the psa exists in the PSAM API, and in the PSAR API
    """
    print '[INFO] list psa '
    url=base_url+'images/'
    params={}
    if args.project_name:
        print '[INFO] list psa ' + args.project_name
	params['psa_id']=args.project_name
    if token:
          params['token']=token
    r=get (url, params=params)
    data=json.loads(str(r.text))
    print json.dumps(data, sort_keys=True, indent=2)
     
    

def remove(args):
    """
    Block and remove completely the PSA from the system. 
    API methods called: PSAM PSA remove API. 
    Locally also remove the project folder and content files
    """
    print '[INFO] Removing project:'+args.project_name
        
    try:
        #Getting project path from the database.
        path = getProjectPath(args.project_name)
	print path
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            #return 0

        print '[INFO] Path for '+args.project_name+' is:'+path
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0
    try:
       	removeDirectory(path)
        print '[INFO] Removed project from:'+path
	#return 0
    except Exception as e:
        print e
        print '[ERROR] Could not remove project files. Please manually remove project from:'+path


    try:
        url=base_url+'images/'+args.project_name
	params={}
	if token:
		params['token']=token
	r=delete (url, params=params)
	print str(r)
        print '[INFO] Removed '+args.project_name+' from PSAM-API'
    except Exception as e:
        print e
        print '[ERROR] Could not remove project from database. Exiting.'
        return 0

    try:
        deleteProject( args.project_name)
        print '[INFO] Removed '+args.project_name+' from database'
    except Exception as e:
        print e
        print '[ERROR] Could not remove project from database. Exiting.'
        return 0
    
    
def publish(args):
    """
    Upload the zip file through the publish PSAM API
    """
    path = getProjectPath(args.project_name)
    #print path
    if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0

    try:
	params={}
	if token:
		params['token']=token
	with open(path, 'rb') as f:
	       	print '[INFO] Publish '+args.project_name+' from PSAM-API'
		#print f
		files={'file':f}
		url=base_url+'images/'+args.project_name+'/'
		#print url
		r=put (url,files=files, params=params)
		print str(r)
		print '[INFO] Publish project: '+args.project_name+' from PSAM-API'
		data=json.loads(r.text)
		if (data['info']!=""):
			print data['info']
		if (data['manifest']!=""):
			print data['manifest']
		if data['plugin']:
			print data['plugin']
		if (data['info_image']!=""):
			print data['info_image']
		if (data['info_manifest']!=""):
			print data['info_manifest']
		if (data['info_plugin']!=""):
			print data['info_plugin']
		if (data['info_dyn_conf']!=""):
			print data['info_dyn_conf']

	return 0
    except Exception as e:
       	print e
       	print '[ERROR] Could not publish project.'
       	return 0



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
''' 
Adding support for the commands required for the psam-onboard:
1.init
2.remove
3.publish
4.list
'''
parser_init = subparsers.add_parser('init', description="Initialize a project")
parser_init.add_argument('project_name', type=str, help="The name of the project to be initialized.")
parser_init.add_argument('--path', type=str, help="Optional: A specific path in where is the project.")
parser_init.set_defaults(func=init)

parser_remove= subparsers.add_parser('remove', description="Removes the project specified by the user by deleting all relevant files and folders.")
parser_remove.add_argument('project_name', type=str, help="The name of the project to be removed.")
parser_remove.set_defaults(func=remove)

parser_list= subparsers.add_parser('list', description="Check if exist one PSA with the same name that project_name.")
parser_list.add_argument('--project_name', type=str, help="The name of the project to be listed.")
parser_list.set_defaults(func=list)

parser_publish= subparsers.add_parser('publish', description="Publish the project specified by the user.")
parser_publish.add_argument('project_name', type=str, help="The name of the project to be published.")
parser_publish.set_defaults(func=publish)

parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()
args.func(args)

