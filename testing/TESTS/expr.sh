#!/bin/bash

## creating
typeset -i X=8
X_INDICES=$(get_indices $X)
typeset -i Y=10
Y_INDICES=$(get_indices $Y)
typeset -i bytes_float16=2
typeset -i bytes_float32=4
typeset -i bytes_float64=8

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

test_prex "rubik -o a_{shape}.{format} -- $expr_args"
check_file_exists_and_has_size a_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))

test_prex "rubik -o b_{shape}.{format} @${expr_file}"
check_file_exists_and_has_size b_${X}x${Y}.raw $(( $X * $Y * ${bytes_float32} ))
check_files_are_equal a_${X}x${Y}.raw b_${X}x${Y}.raw

