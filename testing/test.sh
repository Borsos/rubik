#!/bin/bash

EMPTY=" "

function prex {
    typeset    _command="$1"
    typeset -i _returncode
    echo ">>> $_command ..." 1>&2
    eval "$_command" ; _returncode=$?
    echo "<<< $_command [${_returncode}]" 1>&2
    return $_returncode
}

function get_matching_tests {
    typeset _pattern="$1"
    typeset _tests=" "
    typeset _test
    typeset _filename
    for _filename in $(get_test_file "$_pattern") ; do
        _test=$(basename "$_filename" | sed 's/\.sh$//g')
        _tests="$_tests$_test "
    done
    echo "$_tests"
}

function get_test_file {
    typeset _test="$1"
    echo "$TESTING_DIR/TESTS/${_test}.sh"
}

AVAILABLE_TESTS=$EMPTY
for _test in $( get_matching_tests '*' ) ; do
    AVAILABLE_TESTS="$AVAILABLE_TESTS$_test "
done

PREPEND_RUBIK_OPTIONS=" "
function prepend_rubik_option {
    PREPEND_RUBIK_OPTIONS="$PREPEND_RUBIK_OPTIONS$1 "
}
APPEND_RUBIK_OPTIONS=" "
function append_rubik_option {
    APPEND_RUBIK_OPTIONS="$APPEND_RUBIK_OPTIONS$1 "
}

TEST_NAME="undefined"
typeset -i TEST_INDEX=-1
typeset -i TEST_NUM=0    # total number of run tests
typeset -i TEST_PROG=0   # number of run tests for test $TEST_NAME
function set_test_name {
    TEST_NAME="$1"
    TEST_INDEX=-1
    TEST_PROG=0
}

function test_prex {
    typeset    _command="rubik ${PREPEND_RUBIK_OPTIONS} $1 ${APPEND_RUBIK_OPTIONS}"
    TEST_INDEX=$(( $TEST_INDEX + 1 ))
    TEST_NUM=$(( $TEST_NUM + 1 ))
    TEST_PROG=$(( $TEST_PROG + 1 ))
    echo "$_command" > ${TEST_NAME}.${TEST_INDEX}.command
    typeset -i _returncode
    prex "$_command" 1> ${TEST_NAME}.${TEST_INDEX}.eo 2>&1 ; _returncode=$?
    return $_returncode
}

typeset -i ERRORS=0
function set_error {
    ERRORS=$(( $ERRORS + 1 ))
}

function die {
    typeset    _message="$1"
    typeset -i _exitcode=${2:-1}
    echo "=== LAST COMMAND: ==="
    cat ${TEST_NAME}.${TEST_INDEX}.command
    cat ${TEST_NAME}.${TEST_INDEX}.eo
    echo "ERR: $_message [exiting ${_exitcode}]" 1>&2
    set_error
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

function check_file_has_content {
    typeset _filename="$1"
    typeset _filecontent="$2"
    typeset _content=$(cat "$_filename" 2>&1)
    if [[ $_filecontent == "$_content" ]] ; then
        echo ".... OK, $_filename has content <${_filecontent}>"
    else
        die "file $_filename has content <${_content}> != expected content <${_filecontent}>"
    fi
}

function check_file_exists_and_has_size {
    typeset _filename="$1"
    typeset _filesize="$2"
    check_file_exists "$_filename"
    check_file_has_size "$_filename" "$_filesize"
}

function check_file_exists_and_has_content {
    typeset _filename="$1"
    typeset _filecontent="$2"
    check_file_exists "$_filename"
    check_file_has_content "$_filename" "$_filecontent"
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

