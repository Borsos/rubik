#!/bin/bash

## creating
typeset -i X=2
X_INDICES=$(get_indices $X)
typeset -i Y=5
Y_INDICES=$(get_indices $Y)
typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

typeset -i XY=$(( $X * $Y ))
SHAPE="${X}x${Y}"

cat > a.expr <<EOF_A
_r = cb.const_cube("${X}x${Y}", value=0.0)

_r[0, 2] = 1.0e-23
_r[0, 4] = 1.0e-15

_r[1, :] = 3.0
_r[1, 2] = 3.03
_r[1, 3] = 300.0
EOF_A

cat > b.expr <<EOF_B
_r = cb.const_cube("${X}x${Y}", value=0.0)

_r[0, 1] = 1.0e-23
_r[0, 3] = 1.0e-15

_r[1, :] = 3.0
_r[1, 1] = 3.03
_r[1, 4] = 300.0
EOF_B

test_prex "-o cubes_a_{shape}.{format} @a.expr"
check_file_exists_and_has_size cubes_a_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-o cubes_b_{shape}.{format} @b.expr"
check_file_exists_and_has_size cubes_b_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-o cubes_r0_{shape}.{format} -i cubes_a_{shape}.{format} -i cubes_b_{shape}.{format} -s ${SHAPE} 'cb.reldiff_cube(i0, i1)'"
check_file_exists_and_has_size cubes_r0_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-o cubes_n0_{shape}.{format} -i cubes_r0_{shape}.{format} -s ${SHAPE} 'cb.nonzero_cube(i0)'"
check_file_exists_and_has_size cubes_n0_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-i cubes_n0_{shape}.{format} -s ${SHAPE} 'np.sum(i0)' --print > sum.n0"
check_file_exists_and_has_content sum.n0 "8.0"

test_prex "-o cubes_r1_{shape}.{format} -i cubes_a_{shape}.{format} -i cubes_b_{shape}.{format} -s ${SHAPE} 'cb.reldiff_cube(i0, i1, in_threshold=1.0e-20)'"
check_file_exists_and_has_size cubes_r1_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-o cubes_n1_{shape}.{format} -i cubes_r1_{shape}.{format} -s ${SHAPE} 'cb.nonzero_cube(i0)'"
check_file_exists_and_has_size cubes_n1_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-i cubes_n1_{shape}.{format} -s ${SHAPE} 'np.sum(i0)' --print > sum.n1"
check_file_exists_and_has_content sum.n1 "6.0"

test_prex "-o cubes_r2_{shape}.{format} -i cubes_a_{shape}.{format} -i cubes_b_{shape}.{format} -s ${SHAPE} 'cb.reldiff_cube(i0, i1, in_threshold=1.0e-20, out_threshold=0.02)'"
check_file_exists_and_has_size cubes_r2_${SHAPE}.raw $(( $XY * $bytes_float32 ))

test_prex "-o cubes_n2_{shape}.{format} -i cubes_r2_{shape}.{format} -s ${SHAPE} 'cb.nonzero_cube(i0)'"
check_file_exists_and_has_size cubes_n2_${SHAPE}.raw $(( $XY * $bytes_float32 ))


test_prex "-i cubes_n2_{shape}.{format} -s ${SHAPE} 'np.sum(i0)' --print > sum.n2"
check_file_exists_and_has_content sum.n2 "4.0"

