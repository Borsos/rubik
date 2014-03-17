#!/bin/bash

function prex {
    typeset    _command="$1"
    typeset -i _returncode
    echo ">>> $_command ..." 1>&2
    eval "$_command" ; _returncode=$?
    echo "<<< $_command [${_returncode}]" 1>&2
    return $_returncode
}

TEST_NAME="undefined"
function set_test_name {
    TEST_NAME="$1"
}

typeset -i INDEX=0
function test_prex {
    typeset    _command="$1 $CUBIST_OPTIONS"
    echo "$_command" > test_command.${TEST_NAME}.${INDEX}
    INDEX=$(( $INDEX + 1 ))
    typeset -i _returncode
    prex "$_command" ; _returncode=$?
    return $_returncode
}

function die {
    typeset    _message="$1"
    typeset -i _exitcode=${2:-1}
    echo "ERR: $_message [exiting ${_exitcode}]" 1>&2
    exit $_exitcode
}

function get_indices {
    typeset -i _num=$1
    typeset    _indices=" "
    typeset -i _i=0
    while [[ $_i -lt $_num ]] ; do
        _indices="$_indices$_i "
        _i=$(( $_i + 1 ))
    done
    echo "$_indices"
}

function check_file_exists {
    typeset _filename="$1"
    if [[ -f "$_filename" ]] ; then
        echo ".... OK, $_filename exists"
    else
        die "file $_filename does not exists"
    fi
}

function check_file_has_size {
    typeset _filename="$1"
    typeset _filesize="$2"
    typeset _statsize=$(stat --printf %s "$_filename")
    if [[ $_filesize -eq $_statsize ]] ; then
        echo ".... OK, $_filename has size ${_filesize}"
    else
        die "file $_filename has size ${_statsize} != expected size ${_filesize}"
    fi
}

function check_file_exists_and_has_size {
    typeset _filename="$1"
    typeset _filesize="$2"
    check_file_exists "$_filename"
    check_file_has_size "$_filename" "$_filesize"
}

function check_files_are_equal {
    typeset _filename_a="$1"
    typeset _filename_b="$2"
    if prex "cmp $_filename_a $_filename_b" ; then # 1>/dev/null 2>&1 ; then
        echo ".... OK, $_filename_a and $_filename_b are equal"
    else
        die "file $_filename_a is NOT equal to $_filename_b: $(cmp $_filename_a $_filename_b)"
    fi
}

