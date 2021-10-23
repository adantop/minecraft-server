#!/bin/bash

cd ${BASH_SOURCE%%/*}
screen -dmS %(screenName)s bash -c ./start.sh