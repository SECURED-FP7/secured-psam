Testing
=======

The execute\_test.sh script creates a project named test in the home directory and then performs the following actions:
1. Adds the test\_manifest.xml to the project's directory
2. Adds an MSPL file to the project. The MSPL file used in this testing is for the Bandwidth Control PSA.
3. Adds an M2lPlugin to the project. The M2L Plugin used in this testing is PSA Bandwidth Control's M2LPlugin.
4. Adds a valid PSA qcow2 image.
5. Validats the project.
6. Pcaks the project.
7. Removes the project.
