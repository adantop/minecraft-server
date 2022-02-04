#!/bin/bash

export JAVA_HOME=%(javaHome)s
export PATH=${JAVA_HOME}:${PATH}

cd %(instancePath)s

%(command)s