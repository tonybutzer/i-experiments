#!/bin/bash

IP=`hostname -I | awk '{print $1}'`
source activate pangeo
echo "ssh -N -L 8888:`hostname`:8888  `whoami`@`hostname`"
# cd $HOME
echo ${IP}
(export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/harris/envi55/idl/bin/bin.linux.x86_64; jupyter lab --no-browser --ip=${IP} --port=8888)
