#!/bin/bash 

export MODULE=$1
export OUTPUT_PATH=$2
export ANACONDA_HOME=$3
export DOWNLOAD_LIBRARY=$4

conda create -y --name $1 python=3.8
source $ANACONDA_HOME/etc/profile.d/conda.sh
conda activate $1
pip install elasticsearch
pip install sphinxcontrib.napoleon

if [ "$DOWNLOAD_LIBRARY" = false ]; then
	pip install $MODULE
fi

PYTHONPATH=$PYTHONPATH:../src python ../src/inspect_docstrings_per_module_standalone.py $MODULE $OUTPUT_PATH
conda deactivate
conda remove -y --name $1 --all