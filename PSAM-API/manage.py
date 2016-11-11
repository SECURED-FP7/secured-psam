#!/usr/bin/env python
import os
import sys

version='0.1'

if __name__ == "__main__":
    if sys.argv[1]=="runserver":
	import logging
	logging.basicConfig(filename='PSAM.log',format='%(asctime)s %(message)s', level=logging.INFO)
	logging.info('Running PSAM with version %s',version)



    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psam.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
