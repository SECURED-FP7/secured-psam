'''
@author: Savvas Charalambides
@note: created on 19/02/2016
@version: 1.0

PSAM-Project Code
-----------------

This tool allows the definition of a new PSA project that will include all the required files. A new
project definition will be able to be performed outside of SECURED on any machine (for example
in the developer local server). Portability can be achieved with the 'pack' command that will allow
the transfer of all of the project's info to another system.
'''

import argparse
import sqlite3, os, sys


tableName = 'psam_projects'
tool_path_dir = os.path.realpath(__file__).split('psam-project.py')[0]
dbName = tool_path_dir+'Utilities/PSAM_PROJECTS.db'

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
    return os.path.exists(path)

'''
Deletes the given directory with all its contents.
'''
def removeDirectory(path):
    import shutil
    shutil.rmtree(path)
    
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

def create(args):
    print '[INFO] Creating new project:'+args.project_name
    path = args.path
    
    if path is None:
        '''
        If the user has not given a path to place the new project
        the project is started in his home directory.
        '''
        from os.path import expanduser
        path = expanduser("~")
    
    '''
    1. We first validate whether the path to create the project is valid.
    2. If the path is valid we check that there is no other project with the same name.
    3. If no other project exists we create the folder which will contain all of the projects files
    4. We add an entry to the database for the project that contains the path on the local filesystem. if an error occurred 
       during the database insert we also remove the project's directory.
    '''    
    if validatePath(path):
        if validatePath(path+'/'+args.project_name):
            print '[ERROR] Project already exists.'
            return 0
        
        try:
            print '[INFO] Creating project at:'+path+'/'+args.project_name
            os.mkdir(path+'/'+args.project_name)
            print "[INFO] Created the project at:"+path+'/'+args.project_name
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
            if (removeDirectory(path+'/'+args.project_name)):
                print '[INFO] Cleared project data.'
            else:
                print '[ERROR] Could not remove project files and folders. Please remove manually the project directory and data.'
            return 0              
    else:
        print '[ERROR] The given path does not exist.'

def remove(args):
    print '[INFO] Removing project:'+args.project_name
    try:
        #Getting project path from the database.
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0  
    
    try:
        print '[INFO] Removing '+args.project_name+' from database'
        deleteProject( args.project_name)
        print '[INFO] Removed '+args.project_name+' from database'
    except Exception as e:
        print e
        print '[ERROR] Could not remove project from database. Exiting.'
        return 0  
    
    try:
        print '[INFO] Removing project from:'+path+'/'+args.project_name
        removeDirectory(path+'/'+args.project_name)
        print '[INFO] Removed project from:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not remove project files. Please manually remove project from:'++path+'/'+args.project_name
        return 0 
    
def addMspl(args):
    templateMSPL=tool_path_dir+'Utilities/template_mspl.xml'
    msplPath = args.file
    useTemplate = False
    
    '''
    if no mspl file was given we use a template manifest.
    '''
    if msplPath is None:
        print '[INFO] No mspl file specified. Trying to use the template mspl:'+os.getcwd()+'/'+templateMSPL
        msplPath=os.getcwd()+'/'+templateMSPL
        useTemplate = True
        
    print '[INFO] Adding mspl:'+msplPath+' for project:'+args.project_name
    
    
    '''
    Getting the path for the project in order to copy the plug-in
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0  
    
    '''
    After getting the project's base directory:
    1. We validate that the mspl file exists
    2. We validate the the mspl file's name ends  with _mspl.xml
    3. We copy the mspl file to the project's directory. If an mspl file with same name already exists it will be OVERWRITTEN.
    '''
    try:
        print '[INFO] Checking if manifest path:'+msplPath+' is valid.'
        '''
        Checking of the path to the manifest is valid and that the file exists.
        if not, we abort the procedure.
        '''
        if validatePath(msplPath):
            print '[INFO] Manifest path:'+msplPath+', is a valid path'
        else:
            print '[ERROR] Manifest path:'+msplPath+', does not exist.'
            print 'Aborting add-mspl.'
            return 0
        
        '''
        Checking if the mspl file's name ends with _mspl.xml.
        If it is not, we abort the procedure.
        '''
        if not useTemplate and ('_mspl.xml' not in msplPath.split('/')[-1]):
            print '[ERROR] Wrong mspl file name. The mspl file name must end with _mspl.xml'
            print 'Aborting add-mspl.'
            return 0
        
        '''
        if we use the template mspl we adjust the destination path (dstPath) so that the mspl name will be: <ProjectName>_mspl.xml
        
        if we do not use the template mspl and one was specified by the user we check if the file ends with _mspl.xml. If not, we adjust the
        destination path (dstPath) so that it ends with that suffix.
        '''
        
        
#         if useTemplate:
#             dstPath = path+'/'+args.project_name+'/'+args.project_name+'_mspl.xml'
#         else:
#             dstPath = path+'/'+args.project_name
            
        if useTemplate:
            dstPath = path + '/' + args.project_name + '/' + args.project_name + '_mspl.xml'
        else:                
                filePath, fileExtension = os.path.splitext(msplPath)
                msplName = filePath.split('/')[-1]
                if msplName.endswith('_mspl') and fileExtension == '.xml':
                    dstPath = path + '/' + args.project_name
                elif  msplName.endswith('_mspl'):
                    dstPath = path + '/' + args.project_name + '/' + msplName + '.xml'
                else:
                    dstPath = path + '/' + args.project_name + '/' + msplName + '_mspl.xml'
            
        
        
        '''
        Finally we try to copy the mspl file to the project's directory.
        '''    
        print '[INFO] Adding mspl:'+msplPath 
        import shutil
        shutil.copy2(msplPath, dstPath)
        print '[INFO] Added mspl:'+msplPath 
    except Exception as e:
        print e
        print '[ERROR] Could not add mspl. Exiting.'
        return 0  
    
def addManifest(args):
    print '[INFO] Adding Manifest file.'
    templateManifest=tool_path_dir+'Utilities/PSAManifest.xml'
    manifestPath = args.file
    useTemplate = False
    
    '''
    if no manifest was given we use a template manifest.
    '''
    if manifestPath is None:
        print '[INFO] No manifest specified. Trying to use the template manifest:'+os.getcwd()+'/'+templateManifest
        manifestPath=os.getcwd()+'/'+templateManifest
        useTemplate = True
        
    print '[INFO] Adding manifest:'+manifestPath+' for project:'+args.project_name
    
    
    '''
    Getting the path for the project in order to add the manifest file
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0  
    
    '''
    After getting the project's base directory:
    1. We validate that the manifest exists
    <Removed since now we use xml manifest and the json manifest>2. We validate that the manifest's name is the same as the project's name
    3. We copy the manifest to the project's directory. If a manifest already exists it will be OVERWRITTEN.
    '''
    try:
        print '[INFO] Checking if manifest path:'+manifestPath+' is valid.'
        '''
        Checking if the path to the manifest is valid and that the file exists.
        if not, we abort the procedure.
        '''
        if validatePath(manifestPath):
            print '[INFO] Manifest path:'+manifestPath+', is a valid path'
        else:
            print '[ERROR] Manifest path:'+manifestPath+', does not exist.'
            print 'Aborting add-manifest.'
            return 0
        
#         '''
#         Checking if the manifest's name is the same as the projects name.
#         If it is not, we abort the procedure.
#         '''
#         if not useTemplate and (manifestPath.split('/')[-1] != args.project_name):
#             print '[ERROR] Wrong manifest name. Manifest name must be:',args.project_name
#             print 'Aborting add-manifest.'
#             return 0
        '''
        if we use the template manifest we adjust the destination path (dstPath) so that the manifest name will be: <ProjectName>_manifest.xml
        
        if we do not use the template manifest and one was specified by the user we check if the file ends with _manifest.xml. If not, we adjust the
        destination path (dstPath) so that it ends with that suffix.
        '''
        if useTemplate:
            dstPath = path + '/' + args.project_name + '/' + args.project_name + '_manifest.xml'
        else:                
                filePath, fileExtension = os.path.splitext(manifestPath)
                manifestName = filePath.split('/')[-1]
                if manifestName.endswith('_manifest') and fileExtension == '.xml':
                    dstPath = path + '/' + args.project_name
                elif  manifestName.endswith('_manifest'):
                    dstPath = path + '/' + args.project_name + '/' + manifestName + '.xml'
                else:
                    dstPath = path + '/' + args.project_name + '/' + manifestName + '_manifest.xml'
            
        print '[INFO] Trying to remove previous manifest files.'
        try: 
            removeFileBySuffix(['_manifest.xml'],path+'/'+args.project_name)
        except Exception as e:
            print e
            print '[ERROR] Could not remove previous manifest files. Exiting.'
            return 0 
            
        print '[INFO] Removed previous manifest files.'
                
        '''
        Finally we try to copy the manifest file to the project's directory.
        '''    
        print '[INFO] Adding manifest:'+manifestPath 
        import shutil
        shutil.copy2(manifestPath, dstPath)
        print '[INFO] Added manifest:'+manifestPath+' to: '+dstPath 
    except Exception as e:
        print e
        print '[ERROR] Could not add manifest. Exiting.'
        return 0  
    
def addPlugin(args):
    print '[INFO] Adding plug-in:'+args.file+' for project:'+args.project_name
    filePath = args.file
    
    '''
    Getting the path for the project in order to copy the plug-in
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0  
    
    '''
    After getting the project's base directory:
    1. We validate that the plug-in exists
    2. We validate that the plug-in is a jar file
    2. We copy the plug-in to the project's directory. If a plug-in already exists it will be OVERWRITTEN.
    
    '''
    try:
        print '[INFO] Checking if plug-in path:'+filePath+' is valid.'
        if validatePath(filePath):
            print '[INFO] Plug-in path:'+filePath+', is a valid path'
        else:
            print '[ERROR] Plug-in path:'+filePath+', does not exist.'
            print 'Aborting add-plugin.'
            return 0
        filepath, fileExtension = os.path.splitext(filePath)
        if fileExtension != '.jar':
            print '[ERROR] Wrong plug-in name. Plug-in name must be a jar file'
            print 'Aborting add-plugin.'
            return 0
          
        print '[INFO] Trying to remove previous M2L plug-in files.'
        try: 
            removeFileBySuffix(['.jar'],path+'/'+args.project_name)
        except Exception as e:
            print e
            print '[ERROR] Could not remove previous M2L plug-in files. Exiting.'
            return 0 
            
        print '[INFO] Removed previous M2L plug-in files.'
          
        print '[INFO] Adding plug-in:'+filePath 
        import shutil
        shutil.copy2(filePath, path+'/'+args.project_name)
        print '[INFO] Added plug-in:'+filePath+' to: '+path+'/'+args.project_name+'/'+filePath.split('/')[-1] 
    except Exception as e:
        print e
        print '[ERROR] Could not add plug-in. Exiting.'
        return 0  

def add_config(args):
	dyn_confPath=args.file
	try:
		path=getProjectPath(args.project_name)
		if path is None:
			print '[ERROR] Project does not exist. Exiting.'
			return 0
		if validatePath(dyn_confPath):
			print '[INFO] Dynamic configuration path: '+ dyn_confPath+ ', is a valid path'
		else:
			print '[ERROR] Dynamic configuration path: ' +dyn_confPath+ ', does not exist'
			print 'Aborting add-config'
			return 0

		try:
			with open(dyn_confPath) as data_file:
				import json
                        	dataJson=json.load(data_file)
                        for e in dataJson:
                                location=e["location"]
                                dynamic_conf=e["dyn_conf"]
		except:
			print '[ERROR] Wrong dynamic configuration file'
			return 0

		dstPath=path+'/'+args.project_name+'/dyn_conf.txt'
		import shutil
		shutil.copy2(dyn_confPath, dstPath)
		print '[INFO] Added dynamic configuration'
	except Exception as e:
		print e
		print '[ERROR] Could not add dynamic configuration. Exiting'
		return 0
    
def validate(args):
    print '[INFO] Validating project:'+args.project_name
    '''
    Getting the path for the project in order to validate the project
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0
    '''
    Creating the validator instance to start the project validation
    '''
    from ProjectValidator import ProjectValidator
    validator  = ProjectValidator(path+'/'+args.project_name, args.project_name, tool_path_dir)
    
    try:
        if validator.validateProject():
            print '[INFO] Project has been successfully validated.'
        else:
            print '[ERROR] Project has not been successfully validated.'
    except Exception as e:
        print str(e)
        print type(e)
        print e.args
        print sys.exc_info()[0]
        print '[ERROR] Project has not been successfully validated.' 
    
def pack(args):
    print '[INFO] Packing project:'+args.project_name
    
    '''
    Getting the path for the project in order to pack the project
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0
    #Getting the name for the zip file. If user did not give
    #a name for the zip file we use the project's name instead 
    if args.filename is None:
        zipFileName = args.project_name
    else:
         zipFileName = args.filename
    print '[INFO] Trying to pack project:'+args.project_name
    try:
        import shutil
        shutil.make_archive(zipFileName, 'zip', path+'/'+args.project_name)
        shutil.move(zipFileName+'.zip', path+'/'+args.project_name)
    except Exception as e:
        print e
        print '[ERROR] Could not pack project. Exiting.'
        return 0
    print '[INFO] Successfully packed project:'+args.project_name
    print '[INFO] Zip file available at:'+path+'/'+args.project_name
    
def addImage(args):
    print '[INFO] Adding image:'+args.file+' for project:'+args.project_name
    filePath = args.file
    
    '''
    Getting the path for the project in order to copy the image
    ''' 
    try:
        path = getProjectPath(args.project_name)
        if path is None:
            print '[ERROR] Project does not exist. Exiting.'
            return 0
        
        print '[INFO] Path for '+args.project_name+' is:'+path+'/'+args.project_name
    except Exception as e:
        print e
        print '[ERROR] Could not get path for project. Exiting.'
        return 0  
    
    '''
    After getting the project's base directory:
    1. We validate that the image exists
    2. We validate that the image is either an img or qcow2 file
    3. If the image is qcow2 we check it for integrity using qemu-img.
    4. We copy the image to the project's directory. If an image already exists it will be OVERWRITTEN.
    
    '''
    try:
        print '[INFO] Checking if image path:'+filePath+' is valid.'
        if validatePath(filePath):
            print '[INFO] Image path:'+filePath+', is a valid path'
        else:
            print '[ERROR] Image path:'+filePath+', does not exist.'
            print 'Aborting add-image.'
            return 0
        filepath, fileExtension = os.path.splitext(filePath)
        if fileExtension != '.img' and fileExtension != '.qcow2':
            print '[ERROR] Wrong image file. Image must be either .img or .qcow2'
            print 'Aborting add-image.'
            return 0
        if fileExtension == '.qcow2':
            print '[INFO] Checking if image '+filePath+' contains any errors.'
            try:
                from subprocess import STDOUT,Popen,PIPE
                out,err = Popen('qemu-img check '+filePath, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
                
                if err is not None:
                    print '[ERROR] The image contains errors.'
                    print '[ERROR] ',err
                    print '[ERROR] Exiting'
                    return 0
                
                if 'ERROR' in out:
                    print '[ERROR] The image contains errors.'
                    print '[ERROR] ',out
                    print '[ERROR] Exiting'
                    return 0
                
                if 'command not found' in out:
                    print '[INFO] Did not check image: qem-img is not installed.'
            except Exception as e2:
                    print '[ERROR] The image contains errors.'
                    print '[ERROR] ',e2
                    print '[ERROR] Exiting'
                    return 0
            print '[INFO] Image '+filePath+' does not contain any errors.'
        
        print '[INFO] Trying to remove previous PSA image files.'
        try: 
            removeFileBySuffix(['.img','.qcow2'],path+'/'+args.project_name)
        except Exception as e:
            print e
            print '[ERROR] Could not remove previous PSA image files. Exiting.'
            return 0 
            
        print '[INFO] Removed previous PSA image files.'
          
        print '[INFO] Adding image:'+filePath 
        import shutil
        shutil.copy2(filePath, path+'/'+args.project_name)
        print '[INFO] Added image:'+filePath+' to: '+path+'/'+args.project_name+'/'+filePath.split('/')[-1] 
    except Exception as e:
        print e
        print '[ERROR] Could not add image. Exiting.'
        return 0  
        
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
''' 
Adding support for the commands required for the psa-project:
1.create
2.remove
3.add-manifest
4.add-mspl
5.add-plugin
6.validate
7.pack
8.add-image
9.add-config
'''
parser_create = subparsers.add_parser('create', description="Create a project in ~/project-name/ or in the path specified with --path")
parser_create.add_argument('project_name', type=str, help="The name of the project to be created.")
parser_create.add_argument('--path', type=str, help="Optional: A specific path where the project should be created.")
parser_create.set_defaults(func=create)

parser_remove= subparsers.add_parser('remove', description="Removes the project specified by the user by deleting all relevant files and folders.")
parser_remove.add_argument('project_name', type=str, help="The name of the project to be removed.")
parser_remove.set_defaults(func=remove)

parser_addManifest= subparsers.add_parser('add-manifest', formatter_class=argparse.RawDescriptionHelpFormatter, description="Registers locally the PSA manifest. More precisely:\n\t-If <file> is provided for the optional <file> parameter, the tool copies in the correct folder the <file>.\n\t-If the optional <file> parameter is omitted, then the tool should create an empty manifest template that should be adjusted by the developer.")
parser_addManifest.add_argument('project_name', type=str,help="The name of the project for which to add the Manifest.")
parser_addManifest.add_argument('--file', type=str, help="Optional:The path towards the Manifest file to be added.")
parser_addManifest.set_defaults(func=addManifest)

parser_addMSPL= subparsers.add_parser('add-mspl', formatter_class=argparse.RawDescriptionHelpFormatter,description="Register locally an example of MSPL. If more than one MSPL file is available, then the command can execute several times. Similar to add-manifest:\n\t-If the file is provided for the optional <file> parameter, the tool copies in the correct folder the <file>.\n\t-If the optional <file> parameter is omitted, then the tool creates an empty MSPL template that should be adjusted by the developer.")
parser_addMSPL.add_argument('project_name', type=str, help="The name of the project for which to add the MSPL.")
parser_addMSPL.add_argument('--file', type=str, help="Optional:The path towards the MSPL file to be added.")
parser_addMSPL.set_defaults(func=addMspl)

parser_addPlugin= subparsers.add_parser('add-plugin', description="Register locally an M2L plug-in for the PSA.")
parser_addPlugin.add_argument('project_name', type=str, help="The name of the project for which to add the M2L plug-in.")
parser_addPlugin.add_argument('file', type=str, help="The path towards the M2L plug-in file to be added.")
parser_addPlugin.set_defaults(func=addPlugin)

parser_validate= subparsers.add_parser('validate', formatter_class=argparse.RawDescriptionHelpFormatter, description="The validate command executes the following actions:\n\t\t-Checks that all of the following 3 files are present: Manifest, M2L plug-in, PSA image.\n\t\t-Validates the Manifest's format.\n\t\t-Cross checks that the PSA image filename and M2L plug-in filename pointed by the Manifest exist in the local path store.\n\t\t-Plug-in validation with all provided MSPL.")
parser_validate.add_argument('project_name', type=str, help="The name of the project to Validate.")
parser_validate.set_defaults(func=validate)

parser_pack= subparsers.add_parser('pack', description="Create a package with all the files in a zipped format to allow migration to other servers.")
parser_pack.add_argument('project_name', type=str, help="The name of the project for which to pack.")
parser_pack.add_argument('--filename', type=str, help="The name of the zip file to be created")
parser_pack.set_defaults(func=pack)

parser_pack= subparsers.add_parser('add-image', formatter_class=argparse.RawDescriptionHelpFormatter, description="Add the PSA Image file. The image file can be:\n\t-> .img file\n\t-> .qcow2 image")
parser_pack.add_argument('project_name', type=str, help="The name of the project for which to add the image file.")
parser_pack.add_argument('file', type=str, help="The path to the image to be added.")
parser_pack.set_defaults(func=addImage)

parser_pack= subparsers.add_parser('add-config', formatter_class=argparse.RawDescriptionHelpFormatter, description="Add the dynamic configuration to PSA")
parser_pack.add_argument('project_name', type=str, help="The name of the project for which to add the dynamic configuration.")
parser_pack.add_argument('file', type=str, help="The path to the dynamic configuration to be added.")
parser_pack.set_defaults(func=add_config)

parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()
args.func(args)

