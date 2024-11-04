#!/bin/bash

default_python_install="python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt"

declare -A projects=(
    ["21102024-ArXiv"]="cd web; npm install; cd ..;cd server; pip install -r requirements.txt"
    ["rocket"]=default_python_install
    ["send_rcs_message"]=default_python_install
)

for project in "${!projects[@]}"; do
    echo "Installing $project"
    cd $project
    eval ${projects[$project]}
    cd ..
done
