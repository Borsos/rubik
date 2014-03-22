#!/bin/bash

## creating
typeset -i X=8
X_INDICES=$(get_indices $X)
typeset -i Y=10
Y_INDICES=$(get_indices $Y)
typeset -i H=30
typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8
test_prex "cubist -o a_{shape}.{format} -e 'cb.linear_cube(($X, $Y))'"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -o a_{shape}.{format} -e 'cb.linear_cube(($X, $Y))' -Of text"
check_file_exists a_${X}x${Y}.text
test_prex "cubist -i a_{shape}.{format} -s "${X}x${Y}" -o tmp_{shape}.text2{format} -If text -Of raw"
check_file_exists tmp_${X}x${Y}.text2raw
check_files_are_equal a_${X}x${Y}.raw tmp_${X}x${Y}.text2raw

test_prex "cubist -o a_{shape}.{format} -e 'cb.linear_cube(($X, $Y))' -Of csv"
check_file_exists a_${X}x${Y}.csv
test_prex "cubist -i a_{shape}.{format} -s "${X}x${Y}" -o tmp_{shape}.csv2{format} -If csv -Of raw"
check_file_exists tmp_${X}x${Y}.csv2raw
check_files_are_equal a_${X}x${Y}.raw tmp_${X}x${Y}.csv2raw

test_prex "cubist -o b_{shape}.{format} -e 'cb.linear_cube((${X}, ${Y}))'"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -o c_{shape}.{format} -e 'cb.linear_cube((${X}, ${Y}))'"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -o l_{shape}.{format} -e 'cb.linear_cube((${X}, ${Y}))'"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -o a_{shape}.{format} -e 'cb.linear_cube((${X}, ${H}, ${Y}))'"
check_file_exists_and_has_size a_${X}x${H}x${Y}.raw $(( $X * $H * $Y * ${bytes_float32} ))

test_prex "cubist -o f_{shape}.{dtype}.{format} -t float16 -e 'cb.linear_cube((8, 10))'"
check_file_exists_and_has_size f_${X}x${Y}.float16.raw $(( $X * $Y * ${bytes_float16} ))

test_prex "cubist -o g_{shape}.{dtype}.{format} -t float64 -e 'cb.linear_cube((8, 10))'"
check_file_exists_and_has_size g_${X}x${Y}.float64.raw $(( $X * $Y * ${bytes_float64} ))

typeset -i D0=6
typeset -i D1=10
typeset -i D2=5
typeset -i D3=9
typeset -i D4=4
typeset -i D5=12
typeset D6_SHAPE=${D0}x${D1}x${D2}x${D3}x${D4}x${D5}
typeset -i D0f=3
typeset -i D2f=0
typeset -i D4f=1
typeset -i D5f=8
typeset D6_EXTRACTOR=${D0f}x:x${D2f}x:x${D4f}x${D5f}
typeset D2_SHAPE=${D1}x${D3}
test_prex "cubist -o d{rank}_{shape}.{format} -e 'cb.linear_cube(($D0, $D1, $D2, $D3, $D4, $D5))'"
check_file_exists_and_has_size d6_${D6_SHAPE}.raw $(( $D0 * $D1 * $D2 * $D3 * $D4 * $D5 * ${bytes_float32} ))

## checks
test_prex "cubist -i a_{shape}.{format} -i b_{shape}.{format} -s 8x10 -o u_{shape}.{format} -e 'i0 - i1'"
check_file_exists_and_has_size u_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -i a_{shape}.{format} -s 8x30x10 -x :x5x: -o tmp_{shape}.{format}"
check_file_exists_and_has_size tmp_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

## --- different shapes ---
test_prex "cubist -i tmp_{shape}.{format} -i a_{shape}.{format} -s 8x10 -e 'i0 - i1' -o out0_{shape}.{format}"
check_file_exists_and_has_size out0_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -i a_{shape}.{format} -s 8x30x10 -i a_{shape}.{format} -s 8x10 -e 'i0[:, 5, :] - i1' -o out1_{shape}.{format}"
check_file_exists_and_has_size out1_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal out0_${X}x${Y}.raw out1_${X}x${Y}.raw

test_prex "cubist -i a_{shape}.{format} -s 8x30x10 -x i0=:x5x: -i a_{shape}.{format} -s 8x10 -e 'i0 - i1' -o out2_{shape}.{format}"
check_file_exists_and_has_size out2_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal out0_${X}x${Y}.raw out2_${X}x${Y}.raw

## --- different dtypes ---
test_prex "cubist -i f_{shape}.{dtype}.{format} -It float16 -o tmp_f_{shape}.{dtype}.{format} -Ot float64 -s 8x10"
check_file_exists_and_has_size tmp_f_${X}x${Y}.float64.raw $(( $X * $Y * ${bytes_float64} ))

test_prex "cubist -i g_{shape}.{dtype}.{format} -i tmp_f_{shape}.{dtype}.{format} -t float64 -o out0_{shape}.{dtype}.{format} -s 8x10 -e 'i0 - i1'"
check_file_exists_and_has_size out0_${X}x${Y}.float64.raw $(( $X * $Y * ${bytes_float64} ))

test_prex "cubist -i g_{shape}.{dtype}.{format} -It float64 -i f_{shape}.{dtype}.{format} -It float16 -s 8x10 -o out1_{shape}.{dtype}.{format} -e 'i0 - i1' -Ot float64"
check_file_exists_and_has_size out1_${X}x${Y}.float64.raw $(( $X * $Y * ${bytes_float64} ))
check_files_are_equal out0_${X}x${Y}.float64.raw out1_${X}x${Y}.float64.raw

## --- user defined variables ---
test_prex "cubist -i a=a_{shape}.{format} -i b=b_{shape}.{format} -s 8x10 -o r0_{shape}.{format} -e f_a=10.0 -e f_b=-5.0 -e 'f_a * a + f_b * b'"
check_file_exists_and_has_size r0_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "cubist -i a=a_{shape}.{format} -i b=b_{shape}.{format} -s 8x10 -o r1_{shape}.{format} -e c='10.0 * a' -e d='-5.0 * b' -e 'c + d'"
check_file_exists_and_has_size r1_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal r0_${X}x${Y}.raw r1_${X}x${Y}.raw

## --- cubes ---
typeset -i _x=$(( $X - 2 ))

# raw
test_prex "cubist -e 'cb.fromfile_raw(\"a_8x10.raw\", dtype=np.float32, shape=\"8x10\", extractor=\"2:x4\")' -o out10_{shape}.{format}"
check_file_exists_and_has_size out10_${_x}.raw $(( $_x * ${bytes_float32} ))

test_prex "cubist -e 'np.fromfile(\"a_8x10.raw\", dtype=np.float32).reshape((8,10))[2:, 4]' -o out11_{shape}.{format}"
check_file_exists_and_has_size out11_${_x}.raw $(( $_x * ${bytes_float32} ))
check_files_are_equal out10_${_x}.raw out11_${_x}.raw

# csv
test_prex "cubist -e 'cb.fromfile_csv(\"a_8x10.csv\", dtype=np.float32, shape=\"8x10\", extractor=\"2:x4\")' -o out20_{shape}.{format}"
check_file_exists_and_has_size out20_${_x}.raw $(( $_x * ${bytes_float32} ))

test_prex "cubist -e 'np.fromfile(\"a_8x10.csv\", dtype=np.float32, sep=\",\").reshape((8,10))[2:, 4]' -o out21_{shape}.{format}"
check_file_exists_and_has_size out21_${_x}.raw $(( $_x * ${bytes_float32} ))
check_files_are_equal out20_${_x}.raw out21_${_x}.raw

# text
test_prex "cubist -e 'cb.fromfile_text(\"a_8x10.text\", dtype=np.float32, shape=\"8x10\", extractor=\"2:x4\")' -o out30_{shape}.{format}"
check_file_exists_and_has_size out30_${_x}.raw $(( $_x * ${bytes_float32} ))

test_prex "cubist -e 'np.loadtxt(\"a_8x10.text\", dtype=np.float32).reshape((8,10))[2:, 4]' -o out31_{shape}.{format}"
check_file_exists_and_has_size out31_${_x}.raw $(( $_x * ${bytes_float32} ))
check_files_are_equal out30_${_x}.raw out31_${_x}.raw

typeset -i _y=$(( $Y - 2 ))

# raw
test_prex "cubist -e 'cb.fromfile_raw(\"a_8x10.raw\", dtype=np.float32, shape=\"8x10\", extractor=\"4x2:\")' -o out40_{shape}.{format}"
check_file_exists_and_has_size out40_${_y}.raw $(( $_y * ${bytes_float32} ))

test_prex "cubist -e 'np.fromfile(\"a_8x10.raw\", dtype=np.float32).reshape((8,10))[4, 2:]' -o out41_{shape}.{format}"
check_file_exists_and_has_size out41_${_y}.raw $(( $_y * ${bytes_float32} ))
check_files_are_equal out40_${_y}.raw out41_${_y}.raw

# csv
test_prex "cubist -e 'cb.fromfile_csv(\"a_8x10.csv\", dtype=np.float32, shape=\"8x10\", extractor=\"4x2:\")' -o out50_{shape}.{format}"
check_file_exists_and_has_size out50_${_y}.raw $(( $_y * ${bytes_float32} ))

test_prex "cubist -e 'np.fromfile(\"a_8x10.csv\", dtype=np.float32, sep=\",\").reshape((8,10))[4, 2:]' -o out51_{shape}.{format}"
check_file_exists_and_has_size out51_${_y}.raw $(( $_y * ${bytes_float32} ))
check_files_are_equal out50_${_y}.raw out51_${_y}.raw

# text
test_prex "cubist -e 'cb.fromfile_text(\"a_8x10.text\", dtype=np.float32, shape=\"8x10\", extractor=\"4x2:\")' -o out60_{shape}.{format}"
check_file_exists_and_has_size out60_${_y}.raw $(( $_y * ${bytes_float32} ))

test_prex "cubist -e 'np.loadtxt(\"a_8x10.text\", dtype=np.float32).reshape((8,10))[4, 2:]' -o out61_{shape}.{format}"
check_file_exists_and_has_size out61_${_y}.raw $(( $_y * ${bytes_float32} ))
check_files_are_equal out60_${_y}.raw out61_${_y}.raw

## --- filenames ---
typeset -i _x=3
typeset -i _y=2
typeset -i _z=4
test_prex "cubist -e 'cb.linear_cube(($_x, $_y, $_z))' -o a_{shape[0]}_{shape[1]}_{shape[2]}.{format}"
check_file_exists_and_has_size a_${_x}_${_y}_${_z}.raw $(( $_x * $_y * $_z * ${bytes_float32} ))

## --- merge ---
test_prex "cubist -i a=a_{shape}.{format} -i b=b_{shape}.{format} -i c=c_{shape}.{format} -s 8x10 -o res_{shape}.{format} -e 'np.array([a, b, c])'"
check_file_exists_and_has_size res_3x${X}x${Y}.raw $(( 3 * $X * $Y * $bytes_float32 ))

## --- split ---
test_prex "cubist -i a_{shape}.{format} -s 8x10 -o r0_x{d0}_{shape}.{format} --split 0"
for _x in $X_INDICES ; do
    check_file_exists_and_has_size r0_x${_x}_${Y}.raw $(( $Y * $bytes_float32 ))
done

test_prex "cubist -i a_{shape}.{format} -s 8x10 -o r1_y{d1}_{shape}.{format} --split 1"
for _y in $Y_INDICES ; do
    check_file_exists_and_has_size r1_y${_y}_${X}.raw $(( $X * $bytes_float32 ))
done

test_prex "cubist -i a_{shape}.{format} -s 8x10 -o r01_x{d0}_y{d1}.{format} --split 0 --split 1"
for _x in $X_INDICES ; do
    for _y in $Y_INDICES ; do
        check_file_exists_and_has_size r01_x${_x}_y${_y}.raw $(( $bytes_float32 ))
    done
done

## --- multi-dimensional cube ---
test_prex "cubist -i d{rank}_{shape}.{format} -s $D6_SHAPE -x $D6_EXTRACTOR -o d{rank}_d0=${D0f}_d2=${D2f}_d4=${D4f}_d5=${D5f}_{shape}.{format}"
check_file_exists_and_has_size d2_d0=${D0f}_d2=${D2f}_d4=${D4f}_d5=${D5f}_${D2_SHAPE}.raw $(( $D1 * $D3 * $bytes_float32 ))

## --- multiple expressions ---
test_prex "cubist -e 'a10=10' 'b30=a10 * 3' -e 'c50=b30 + 20' --random-seed 100 'd100=c50 * 2' 'd100 - 10' --print > c.out"
check_file_exists_and_has_content c.out '90'
