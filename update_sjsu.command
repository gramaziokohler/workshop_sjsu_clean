#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"
eval "$(conda shell.bash hook)"
conda activate sjsu
python -m pip install --no-deps --force-reinstall update/COMPAS-1.8.1.tar.gz