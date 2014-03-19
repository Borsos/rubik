#!/bin/bash

## creating
typeset -i X=10
X_INDICES=$(get_indices $X)
typeset -i Y=20
Y_INDICES=$(get_indices $Y)
typeset -i Z=30
Z_INDICES=$(get_indices $Z)
typeset -i XYZ=$(( $X * $Y * $Z ))
typeset -i H=501
H_INDICES=$(get_indices $H)
typeset -i XYHZ=$(( $XYZ * $H ))

typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

typeset CONST_VALUE=7.0

typeset -i RANDOM_SEED=100

add_cubist_option "--random-seed $RANDOM_SEED"

test_prex "cubist -e 'cnp.random_cube(\"${X}x${Y}x${Z}\")' -o im_${X}x${Y}x${Z}.raw"
check_file_exists_and_has_size im_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

test_prex "cubist -e 'cnp.random_cube(\"${X}x${Y}x${Z}\")' -o rtmp_{shape}.{format}"
check_file_exists_and_has_size rtmp_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))
check_files_are_equal im_${X}x${Y}x${Z}.raw rtmp_${X}x${Y}x${Z}.raw

test_prex "cubist -e 'cnp.const_cube(\"${X}x${Y}x${Z}\", value=$CONST_VALUE)' -o c_{shape}.{format}"
check_file_exists_and_has_size c_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

test_prex "cubist -i c_{shape}.{format} -s ${X}x${Y}x${Z} -e 'np.sum(i0) - ( $X * $Y * $Z * $CONST_VALUE )' -P > c.out"
check_file_exists_and_has_content c.out 0.0

test_prex "cubist -e 'cnp.linear_cube(\"${X}x${Y}x${Z}\", start=2.0)' -o l_{shape}.{format}"
check_file_exists_and_has_size l_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

test_prex "cubist -e 'np.array([[[k for z in range(${Z})] for j in range(${Y})] for k in range(${X})])' -o cp_{shape}.{format}"
check_file_exists_and_has_size cp_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

test_prex "cubist -e 'cnp.random_cube(\"${X}x${Y}x${H}x${Z}\")' -o og_{shape}.{format}"
check_file_exists_and_has_size og_${X}x${Y}x${H}x${Z}.raw $(( $XYHZ * ${bytes_float32} ))

test_prex "cubist -i og_{shape}.{format} -s 10x20x501x30 -x :x:x250x: -o og_h250_{shape}.{format}"
check_file_exists_and_has_size og_h250_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

Hincr=10
Hnum=11
Hstop=$(( $Hstart + ( $Hincr * $Hnum ) + 1 ))
test_prex "cubist -i og_{shape}.{format} -s ${X}x${Y}x${H}x${Z} -x :x:x${Hstart}:${Hstop}:${Hincr}x: -o og_h{d2}_{shape}.{format} --split 2"
typeset -i i=0
while [[ $i -lt $Hnum ]] ; do
    check_file_exists_and_has_size og_h${i}_${X}x${Y}x${Z}.raw $(( $XYZ * $bytes_float32 ))
    i=$(( $i + 1 ))
done

test_prex "cubist -e 'cnp.const_blocks_cube(\"10x20x30\")' -o cp_{shape}.{format}"
check_file_exists_and_has_size cp_${X}x${Y}x${Z}.raw $(( $XYZ * ${bytes_float32} ))

## --- 2D ---
typeset -i _x=8
typeset -i _y=10
test_prex "cubist -e 'cnp.linear_cube(\"$_x x $_y\")' -o l1_{shape}.{format}"
check_file_exists_and_has_size l1_${_x}x${_y}.raw $(( $_x * $_y * ${bytes_float32} ))

test_prex "cubist -e 'cnp.linear_cube(\"$_x x $_y\", start=1.0, increment=2.0)' -o l2_{shape}.{format}"
check_file_exists_and_has_size l2_${_x}x${_y}.raw $(( $_x * $_y * ${bytes_float32} ))

test_prex "cubist -i l1_{shape}.{format} -i l2_{shape}.{format} -s 8x10 -e 'cnp.equals_num(i0, i1)' -P > res.out"
check_file_exists_and_has_content res.out 0

test_prex "cubist -i l1_{shape}.{format} -i l2_{shape}.{format} -s 8x10 -e 'cnp.equals_num(i0, i1, tolerance=1.0)' -P > res.out"
check_file_exists_and_has_content res.out 1

test_prex "cubist -i l1_{shape}.{format} -i l2_{shape}.{format} -s 8x10 -e 'cnp.equals_num(i0, i1, tolerance=10.0)' -P > res.out"
check_file_exists_and_has_content res.out 10

test_prex "cubist -i l1_{shape}.{format} -i l2_{shape}.{format} -s 8x10 -e 'cnp.equals_num(i0, i1, tolerance=1e3)' -P > res.out"
check_file_exists_and_has_content res.out 80
