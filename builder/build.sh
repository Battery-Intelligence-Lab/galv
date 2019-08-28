#!/bin/bash
echo "
Running docker-builder build.sh
"

function StopIfError() {
exit_status=$1
message=$2
if [ $exit_status -ne 0 ]; then
    SEPARATOR='\n********************************************************************************\n'
    printf "\n${SEPARATOR}\n${TEXT_RED}${message}${TEXT_NC}\n${SEPARATOR}\n"
    exit $exit_status
fi
}

source /workdir/venv/bin/activate
StopIfError $? "Failed to activate python virtual env"

cd /workdir/project
StopIfError $? "Failed to set working directory to project directory"

make init
StopIfError $? "Failed to install python requirements"

pushd libs/galvanalyser-dash-components
StopIfError $? "Failed to set working directory to libs/galvanalyser-dash-components"
npm install
StopIfError $? "Failed to install npm dependencies"
popd
StopIfError $? "Failed to set working directory back to project directory"

make custom-dash-components
StopIfError $? "Failed to make custom-dash-components"

echo "
make protobuf:
"

make protobuf
StopIfError $? "Failed to make protobuf"
