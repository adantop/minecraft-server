#!/bin/bash

cd %(instancePath)s
screen -dmS %(screenName)s bash -c ./start.sh