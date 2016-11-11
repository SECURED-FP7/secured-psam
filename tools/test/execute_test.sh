python ../psam-project.py create --path ~ test
python ../psam-project.py add-manifest --file test_manifest.xml test
python ../psam-project.py add-mspl --file bwcontrol_mspl.xml test
python ../psam-project.py add-plugin test PSA-BWControl.jar
python ../psam-project.py add-image test test.qcow2
python ../psam-project.py validate test
python ../psam-project.py pack test
python ../psam-project.py remove test
