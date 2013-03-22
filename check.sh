#!/usr/bin/env bash

RED=$(tput setab 1)
GREEN=$(tput setab 2)
NORMAL=$(tput sgr0)

exit_ret=0

check_prog() {
    # Args: program name to check that it exists
    local prog_name=$1

    echo -n "Checking for $prog_name....."
    which "$prog_name" >& /dev/null
    local ret=$?
    if [ $ret -ne 0 ]
    then
        echo -e "${RED}Not Found!${NORMAL}"
        exit_ret=1
    else
        echo -e "${GREEN}Found!${NORMAL}"
    fi
    return $ret
}

check_python_module() {
    # Args: python name to check that it exists
    local prog_name=$1

    echo -n "Checking for Python module $prog_name....."
    python -c "import $prog_name" >& /dev/null
    local ret=$?
    if [ $ret -ne 0 ]
    then
        echo -e "${RED}Not Found!${NORMAL}"
        exit_ret=1
    else
        echo -e "${GREEN}Found!${NORMAL}"
    fi
    return $ret
}

check_prog python
check_prog pyflakes
check_prog ipython
check_prog pip
check_python_module cssselect
check_python_module flask
check_python_module py2neo

exit $exit_ret
