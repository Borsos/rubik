#!/bin/bash

## creating
typeset -i X=8
X_INDICES=$(get_indices $X)
typeset -i Y=10
Y_INDICES=$(get_indices $Y)
typeset -i Z=20
Z_INDICES=$(get_indices $Z)
typeset -i XYZ=$(( $X * $Y * $Z ))

SHAPE=${X}x${Y}x${Z}
typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

RANDOM_SEED=100
add_cubist_option "--random-seed $RANDOM_SEED"

test_prex "cubist -e 'cnp.random_cube(\"${SHAPE}\")' -o r_{shape}.{format}"
check_file_exists_and_has_size r_${X}x${Y}x${Z}.raw $(( $XYZ * bytes_float32 ))

test_prex "cubist -e 'cnp.linear_cube(\"${SHAPE}\")' -o l_{shape}.{format}"
check_file_exists_and_has_size l_${X}x${Y}x${Z}.raw $(( $XYZ * bytes_float32 ))

test_prex "cubist -i r_{shape}.{format} -s ${SHAPE} -o r.txt -Of text"
check_file_exists r.txt

test_prex "cubist -i r_{shape}.{format} -s ${SHAPE} -o r_{shape}.{dtype}.{format} -Ot float64"
check_file_exists_and_has_size r_${SHAPE}.float64.raw $(( $XYZ * bytes_float64 ))

test_prex "cubist -i r_{shape}.{format} -s ${SHAPE} -x :,2:-2,: -o rsub_{shape}.{format}"
check_file_exists_and_has_size rsub_${X}x$(( $Y - 4 ))x${Z}.raw $(( $X * ( $Y - 4 ) * $Z * bytes_float32 ))

test_prex "cubist -i r_{shape}.{format} -s ${SHAPE} -x :,::2,::4 -o rsub_{shape}.{format}"
check_file_exists_and_has_size rsub_${X}x5x5.raw $(( $X * 5 * 5 * bytes_float32 ))

