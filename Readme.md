# PSAM provision service

The PSAM provision service is in charge to allow on-boarding PSAs in the system.

The components are the REST web server and additional  support tools.

## PSAM_API
The main Provision service engine and internal interactions with the PSAR are provided by PSAM_API using a DJango engine.
The code and installation process is available at "PSAM-API" folder

## Tools
The code and installation process is available at "tools" folder:

- **psam-project**: helps developers to pack and distribute their PSAs to the production environment.
Also useful for network administrators that need to bring to production environment PSAs after
certification process.

- **psam-onboard**: simplifies the API interactions with PSAM allowing automatize the on-boarding
process.

- **psam-user**: This utility allow massive subscriptions of users and their PSAs.
