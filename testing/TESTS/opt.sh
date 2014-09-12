#!/bin/bash

## creating
typeset -i X=80
X_INDICES=$(get_indices $X)
typeset -i Y=90
Y_INDICES=$(get_indices $Y)
typeset -i Z=70
Z_INDICES=$(get_indices $Z)
typeset -i XYZ=$(( $X * $Y * $Z ))

typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

RANDOM_SEED=100
prepend_rubik_option "--random-seed $RANDOM_SEED"

test_prex "-e 'cb.random_cube(\"${X}x${Y}x${Z}\")' -o x_${X}x${Y}x${Z}.raw"
check_file_exists_and_has_size x_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

shape="${X}x${Y}x${Z}"
for read_threshold_size in '0' '10b' '100gb' ; do
    for extractor in ':x:x:' '::2x::3x::2' '3:-3x10:-10x20:' ':x:x::2' '1x:x:' ':x1x:' ':x:x1' '::2x1x10:' ; do
        prex "rm -f xd.raw xo.raw xs.raw"
        test_prex "-i x_{shape}.{format} -s $shape --read-threshold-size=$read_threshold_size -x $extractor -o xd.raw"
        check_file_exists xd.raw
        test_prex "-i x_{shape}.{format} -s $shape --read-threshold-size=$read_threshold_size -x $extractor -o xo.raw"
        check_file_exists xo.raw
        check_files_are_equal xd.raw xo.raw
        test_prex "-i x_{shape}.{format} -s $shape --read-threshold-size=0 -x $extractor -o xs.raw"
        check_file_exists xs.raw
        check_files_are_equal xd.raw xs.raw
    done
done
