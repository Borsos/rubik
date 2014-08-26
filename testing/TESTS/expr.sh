#!/bin/bash

## creating
typeset -i X=8
X_INDICES=$(get_indices $X)
typeset -i Y=10
Y_INDICES=$(get_indices $Y)
typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

typeset -i EX=2
typeset -i EY=3

expr_file="source.txt"
expr_args=" "
rm -f $expr_file
for line in \
	"a = cb.linear_cube(\"${X}x${Y}\")" \
	'a += 10' \
	'' \
	'a[1, :] += 100' \
	'a[:, 1] -= 100' \
	'' \
	'_r = a' \
    ; do
    echo "$line" >> "$expr_file"
    expr_args="$expr_args'$line' "
done

test_prex "$expr_args -o a_{shape}.{format}"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "@${expr_file} -o b_{shape}.{format}"
check_file_exists_and_has_size b_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal a_${X}x${Y}.raw b_${X}x${Y}.raw

test_prex "-f ${expr_file} -o c_{shape}.{format}"
check_file_exists_and_has_size c_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal a_${X}x${Y}.raw c_${X}x${Y}.raw

expr_file="expr.w"
cat > "${expr_file}" << EOFCAT
a = cb.const_cube('${X}x${Y}', 2)
write_cube(filename='c2_{shape}.{format}', cube=a)
b = cb.const_cube('${X}x${Y}', 3)
write_cube(filename='c3_{shape}.{format}', cube=b)
c = cb.const_cube('${X}x${Y}', 5)
write_cube(filename='c5_{shape}.{format}', cube=c)
write_cube(filename='c2+3_{shape}.{format}', cube=a + b)
EOFCAT

test_prex "-f ${expr_file}"
check_file_exists_and_has_size c2_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_file_exists_and_has_size c3_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_file_exists_and_has_size c5_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_file_exists_and_has_size c2+3_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal c2+3_${X}x${Y}.raw c5_${X}x${Y}.raw
check_files_are_not_equal c2_${X}x${Y}.raw c5_${X}x${Y}.raw

expr_file="expr.r"
cat > "${expr_file}" << EOFCAT
a = read_cube(filename='c2_{shape}.{format}', shape='${X}x${Y}')
b = read_cube(filename='c3_{shape}.{format}', shape='${X}x${Y}')
write_cube(filename='c5bis_{shape}.{format}', cube=a + b)
EOFCAT

test_prex "-f ${expr_file}"
check_file_exists_and_has_size c5bis_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal c5bis_${X}x${Y}.raw c5_${X}x${Y}.raw

expr_file="expr.x"
cat > "${expr_file}" << EOFCAT
a = read_cube(filename='c2_{shape}.{format}', shape='${X}x${Y}', extractor=':$EX,:$EY')
b = read_cube(filename='c3_{shape}.{format}', shape='${X}x${Y}', extractor=':$EX,:$EY')
write_cube(filename='c5ab_{shape}.{format}', cube=a + b)
c = read_cube(filename='c5_{shape}.{format}', shape='${X}x${Y}', extractor=':$EX,:$EY')
write_cube(filename='c5c_{shape}.{format}', cube=c)
write_cube(filename='c5d_{shape}.{format}', cube=c, format='text')
e = read_cube(filename='c5d_{shape}.{format}', format='text', shape='${EX}x${EY}')
write_cube(filename='c5e_{shape}.{format}', cube=e, format='raw')
EOFCAT

test_prex "-f ${expr_file}"
check_file_exists_and_has_size c5ab_${EX}x${EY}.raw $(( $EX * $EY * ${bytes_float32} ))
check_file_exists_and_has_size c5c_${EX}x${EY}.raw $(( $EX * $EY * ${bytes_float32} ))
check_files_are_equal c5ab_${EX}x${EY}.raw c5c_${EX}x${EY}.raw
check_file_exists c5d_${EX}x${EY}.text
check_files_are_equal c5e_${EX}x${EY}.raw c5c_${EX}x${EY}.raw
