#!/bin/bash

## creating
typeset -i X=10
X_INDICES=$(get_indices $X)
typeset -i Y=20
Y_INDICES=$(get_indices $Y)
typeset -i Z=30
Z_INDICES=$(get_indices $Z)
typeset -i XYZ=$(( $X * $Y * $Z ))

typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

typeset -i RANDOM_SEED=100
add_cubist_option "--random-seed $RANDOM_SEED"

test_prex "cubist -e 'cnp.random_cube(\"10x20x30\")' -o r_10x20x30.raw"
check_file_exists_and_has_size r_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

test_prex "cubist -e 'cnp.random_cube(\"10x20x30\")' -o rtmp_{shape}.{format}"
check_file_exists_and_has_size rtmp_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))
check_files_are_equal r_${X}x${Y}x${Z}.raw rtmp_${X}x${Y}x${Z}.raw
