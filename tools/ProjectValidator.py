'''
@author: Savvas Charalambides
@note: created on 19/02/2016
@version: 1.0

This class provides the Validation functionality for the psam-project 
validate command. The main function is validateProject which is called by the
psam-project tool. The ProjectValidator instance requires the path to the project
files and the project's name when instantiated.
'''
import os
class ProjectValidator():

    def __init__(self, projectPath, projectName, tool_path_dir):
        self.path = projectPath
        self.projectName = projectName
        self.projectFiles = self.getProjectFiles()
        self.mandatoryFiles = {}
        self.tool_path_dir = tool_path_dir
        
    def validateProject(self):
        print "[INFO] Validating that all required files exist in the project's sources"
        if not self.areAllFilesPresent():
            return False
        print "[INFO] File Validation: SUCCESS"
        
        print "[INFO] Validating the project's Manifest file"
#         if not self.isManifestFormatValid():
#             return False
        if not self.validateManifest():
            return False
        print '[INFO] Manifest Format Validation: SUCCESS'
        
        print "[INFO] Validating whether image filename and manifest image reference are correct."
#         if not self.imageNameManifestImageCrossCheck():
#             return False
        if not self.isManifestImageNameCorrect():
            return False
        print '[INFO] Image and Manifest cross validation: SUCCESS'
    
        print "[INFO] Validating M2LPlugin."
        if not self.isPluginValid():
            return False
        print '[INFO] M2LPlugin validation: SUCCESS'
            
        
        return True
    '''
    This function uses the PSA's plug-in and the mspl files to validate the plugin.
    '''
    def isPluginValid(self):
        tester = '../Utilities/M2LPluginTester.jar'
        plugin = self.mandatoryFiles['plugin']
	mspl = self.mandatoryFiles['mspl']
	tempconf = '../Utilities/tempconf'
	command = 'java -jar  '+tester+' .'+plugin+' .'+mspl+' '+tempconf
        try:
            from subprocess import STDOUT,Popen,PIPE
            #out,err = Popen('java -jar  '+tester+' '+plugin+' '+mspl+' '+tempconf, cwd=self.path, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
            out,err = Popen(command, cwd=self.path, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
            
            if err is not None:
                print '[ERROR] M2lPlugin validation: FAIL'
                print err
                return False
                
            if 'Exception' in out or 'exception' in out:
                print '[ERROR] M2lPlugin validation: FAIL'
                print out
                return False
        except Exception as e:
            print e
            print '[ERROR] M2lPlugin validation: FAIL'
            return False
        
        return True
            
    '''
    This function checks that the name of the PSA image is the same as the one stated inside the PSA's manifest file.
    '''
    def isManifestImageNameCorrect(self):
        manifest = self.mandatoryFiles['manifest']
        manifestImageName = None
        manifestImageFormat = None
        imageName = self.mandatoryFiles['image'].split('/')[-1]

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
            return False

        if manifestImageFormat is None :
            print '[ERROR] Image and Manifest cross validation: FAIL'
            print '[ERROR] Could not identify PSA Image format from manifest.'
            return False
        elif manifestImageName is None:
            print '[ERROR] Image and Manifest cross validation: FAIL'
            print '[ERROR] Could not identify PSA Image name from manifest.'
            return False
            

        if imageName == (manifestImageName+'.'+manifestImageFormat):
            return True
        else:
            print '[ERROR] Image and Manifest cross validation: FAIL'
            print '[ERROR] Image Name and Manifest reference are different.'
            print '[ERROR] Image Name:',imageName
            print '[ERROR] Image Name in Manifest:',(manifestImageName+'.'+manifestImageFormat)
            return False
    

    '''
    Returns a list of all files in the project's directory.
    '''
    def getProjectFiles(self):
        from os import listdir
        from os.path import isfile, join
        return [join(self.path, f) for f in listdir(self.path) if isfile(join(self.path, f))]
    
    '''
    this functions checks whether all mandatory files are present in the project's home directory.
    '''
    def areAllFilesPresent(self):
        #List containing all required files to be used to cross check that we have identified them
        requiredFiles = ['image','manifest','plugin','mspl']
        
        '''
        Building a dictionary of all files in the project's home directory:
        1.we identify the image by looking for a file with either .img or .qcow2 extension. There can only be ONE image file.
        2.we identify MSPL files by looking for files ending with _mspl.xml.
        3.we identify the manifest by looking for a file that ends with _manifest.xml.
        4. we identify the plug-in by looking for a file that ends with .jar.
        5. all other files that do not fall in any of the above categories we add them in a list
           named unknown_files.
        '''
        for filepath in self.projectFiles:
            fileName, fileExtension = os.path.splitext(filepath)
            fileName = filepath.split('/')[-1]            
            if fileExtension == '.img':
                    if not self.mandatoryFiles.has_key('image'):
                        self.mandatoryFiles['image'] = filepath
                    else:
                        print '[ERROR] File Validation: FAIL'
                        print '[ERROR] More than one image files are present.'
                        return False
            elif fileExtension == '.qcow2':
                    if not self.mandatoryFiles.has_key('image'):
                        self.mandatoryFiles['image'] = filepath
                    else:
                        print '[ERROR] File Validation: FAIL'
                        print '[ERROR] More than one image files are present.'
                        return False
            elif  '_manifest.xml' in fileName:
                if not self.mandatoryFiles.has_key('manifest'):
                    self.mandatoryFiles['manifest'] = filepath
                else:
                    print '[ERROR] File Checking: FAIL'
                    print '[ERROR] More than one manifest files are present.'
                    return False
            elif '_mspl.xml' in fileName:
                try:
                    self.mandatoryFiles['mspl'].append(filepath)
                except KeyError:
                    self.mandatoryFiles['mspl'] = filepath
            elif fileExtension == '.jar':
                if not self.mandatoryFiles.has_key('plugin'):
                    self.mandatoryFiles['plugin'] = filepath
                else:
                    print '[ERROR] File Checking: FAIL'
                    print '[ERROR] More than one plug-in files are present.'
                    return False
            else:
                try:
                    self.mandatoryFiles['unknown_files'].append(filepath)
                except KeyError:
                    self.mandatoryFiles['unknown_files'] = [filepath]
        '''
        After building the project's dictionary we validate that all required files
        are present.
        '''
        for requirement in requiredFiles:
            if not self.mandatoryFiles.has_key(requirement):
                print '[ERROR] File Checking: FAIL'
                print '[ERROR] '+requirement+' was not identified.'
                return False
            
        #A summary of the project's files is printed before exiting 
        print '\n[INFO] File Checking Summary:'
        for key,value in self.mandatoryFiles.items():
            print '\t'+key+': '+str(value)
        return True
    
    '''
    This method validates the xml manifest file using the PSA Manifest xsd schema.
    '''
    def validateManifest(self):
        #Getting the manifest file's path to read its contents
        manifest = self.mandatoryFiles['manifest']
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
            with open(self.tool_path_dir+'Utilities/PSA_manifest.xsd', 'r') as f:
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
    
    
    '''
    **********LEGACY FUNCTION USING JSON MANIFEST**********
    Manifest format validation when manifest file was JSON.
    '''
    def isManifestFormatValid(self):
        import json
        #Getting the manifest file's path to read its contents
        manifest = self.mandatoryFiles['manifest']
        '''
        1. Validating Manifest general json schema
        '''
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
        
        '''
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
        ''' 
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
    def imageNameManifestImageCrossCheck(self):
        import json
        manifest = self.mandatoryFiles['manifest']
        try:
            f = open(manifest,'r')
            data = f.read()
            f.close()
            manifestObject = json.loads(data)
        except Exception as e:
            print e
            print '[ERROR] Image and Manifest cross validation: FAIL'
            print '[ERROR] Cannot load manifst file.'
            return False
        
        manifestImageName = manifestObject['disk']
        imageName = self.mandatoryFiles['image'].split('/')[-1]
        if imageName == manifestImageName:
            return True
        else:
            print '[ERROR] Image and Manifest cross validation: FAIL'
            print '[ERROR] Image Name and Manifest reference are different.'
            print '[ERROR] Image Name:',imageName
            print '[ERROR] Image Name in Manifest:',manifestImageName
            return False
         

