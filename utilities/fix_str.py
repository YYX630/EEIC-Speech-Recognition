#!/usr/bin/env python3
# coding: utf-8
import sys
if __name__ == '__main__':
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    output_file = open(output_file_name, "w")
    counter = 0
    with open(input_file_name) as f:
        for line in f:
            counter += 1
            if counter <= 4:
                continue
            array_line = line.split()
            output_file.write(''.join(array_line[1:len(array_line)-1])+"\n")