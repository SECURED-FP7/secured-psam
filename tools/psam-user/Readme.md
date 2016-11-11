
# User massive subscription
This utility allow massive subscriptions of users and their PSAs. It is based on existing UPR, PSAM and PSAR API and it is offered as client for Network Operators, Corporations, and companies form massive provision process.
# psam-users tool
## Description
This is a auxiliary tool, to be use as a complement for Grandmother GUI for massive or batch user subscriptions.
The tool is file based, you can create a file with hundred of users to be added, or a set of HSPL policies to be applied.
Also it very useful to dump the current information of users and their policies from SECURED and store it in a file, e.g.: backup or migration task.

## Usage:
For use this tool, is necesary that you export the UPR_URL:

	export UPR_URL=UPR_URL
	export PSAR_URL=PSAR_URL
	export SPM_IP=SPM_IP

```
$ python psam-users.py -h
usage: psam-users.py [-h] [-V]
                     {get_user,add_user,delete_user,get_hspl,add_hspl,delete_hspl,get_mspl,add_mspl,delete_mspl,get_psa,add_psa,delete_psa}
                     ...

positional arguments:
  {get_user,add_user,delete_user,get_hspl,add_hspl,delete_hspl,get_mspl,add_mspl,delete_mspl,get_psa,add_psa,delete_psa}

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit

```

### 1.Get_user
Returns in standard output the list of users and their profiles. (JSON). If a file is included then store in the file. 

```

$ python psam-users.py get_user -h
usage: psam-users.py get_user [-h] path

Returns in standard output the list of users and their profiles. (JSON). If a
file is included then store in the file

positional arguments:
  path        A specific path in where is the project.

optional arguments:
  -h, --help  show this help message and exit


```

### 2.Add_user
Provision of all users in the file.  


```
$ python psam-users.py add_user -h
usage: psam-users.py add_user [-h] path

Provision of all users in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit


```
The format of the file will be like this.

	[
	    {
	        "integrityLevel": 1,
	        "is_admin": true,
	        "is_cooperative": true,
        	"is_infrastructure": false,
        	"type": "normal",
        	"user_id": "mother"
    	}
	]

If you have more tags,  they will be ignored.

### 3.Delete_user
Remove of all users in the file. 

```
$ python psam-users.py delete_user -h
usage: psam-users.py delete_user [-h] path

Remove of all users in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit

```

### 4.Get_hspl
Store in the file the list of hspl. 

```
$ python psam-users.py get_hspl -h
usage: psam-users.py get_hspl [-h] path

Store in the file the list of hspl.

positional arguments:
  path        The path of the file.

optional arguments:
  -h, --help  show this help message and exit


```

### 5.Add_hspl
Provision of all hspl in the file.  

```
$ python psam-users.py add_hspl -h
usage: psam-users.py add_hspl [-h] path

Provision of all hspl in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit


```


The format of the file will be like this.

	[
    	{
        	"editor": "mother",
       		"hspl":"mother;prot_conf_integr;Internet_traffic;(type_Content,web)",
        	"target": "mother"
    	}
 	]
	
If you have more tags,  they will be ignored.

### 6.Delete_hspl
Remove of all hspl in the file. 

```
$ python psam-users.py delete_hspl -h
usage: psam-users.py delete_hspl [-h] path

Remove of all hspl in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit


```

### 7.Get_mspl
Store in the file the list of mspl. 

```
$ python psam-users.py get_mspl -h
usage: psam-users.py get_mspl [-h] path

Store in the file the list of mspl.

positional arguments:
  path        The path of the file.

optional arguments:
  -h, --help  show this help message and exit


```

### 8.Add_mspl
Provision of all mspl in the file.  

```
$ python psam-users.py add_mspl -h
usage: psam-users.py add_mspl [-h] path

Provision of all mspl in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit


```

The format of the file will be like this.

	[
    	{
        	"capability": "TLS_protocolreencryptProtection_integrityProtection_confidentiality",
        	"editor": "mother",
        	"is_reconciled": false,
        	"mspl": "PD94bWwgdmVyc2lvbj0iMS4w”,
        	"target": "child"
    	}
	]

	
If you have more tags,  they will be ignored.
### 9.Delete_mspl
Remove of all mspl in the file. 

```
$ python psam-users.py delete_mspl -h
usage: psam-users.py delete_mspl [-h] path

Remove of all mspl in the file

positional arguments:
  path        The path of the file

optional arguments:
  -h, --help  show this help message and exit


```

### 7.Get_psa
Store in the file the list of psa from the user. 

```
$ python psam-users.py get_psa -h
usage: psam-users.py get_psa [-h] path user_id

Store in the file the list of psas

positional arguments:
  path        The path of the file.
  user_id     The name of the user.

optional arguments:
  -h, --help  show this help message and exit


```

### 8.Add_psa
Provision of all psa in the file for a user.

```
$ python psam-users.py add_psa -h
usage: psam-users.py add_psa [-h] path user_id

Provision of all psas in the file for a specific user

positional arguments:
  path        The path of the file
  user_id     The name of the user

optional arguments:
  -h, --help  show this help message and exit


```

The format of the file will be like this.

	[
    	{
        	"active": "True",
        	"psa_id": "reencryptPSA",
        	"running_order": 1
    	}
	]


	
If you have more tags,  they will be ignored.

### 9.Delete_psa
Remove of all psa in the file for a user. 

```
$ python psam-users.py delete_psa -h
usage: psam-users.py delete_psa [-h] path user_id

Remove of all psas in the file

positional arguments:
  path        The path of the file
  user_id     The name of the user.

optional arguments:
  -h, --help  show this help message and exit


```
