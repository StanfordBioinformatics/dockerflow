#!/usr/bin/env python

import re
import sys

# Take file with concatenated flagstat results as input
concat_flagstat_file = sys.argv[1]
series = sys.argv[2]    # Arbitrary index for grouping samples in R ggplot
table_concat_flagstat_file = sys.argv[3]

# Create R formatted table file and add header
OUT = open(table_concat_flagstat_file, 'w')
header_elements = [
                   'series',
                   'sample',
                   'total_reads',
                   'duplicate_reads',
                   'mapped_read_count',
                   'paired_reads',
                   'read1',
                   'read2',
                   'properly_paired',
                   'paired_mate_mapped',
                   'singletons',
                   'mate_mapped_diff_chr',
                   'mate_mapped_diff_chr_mapQ_5']
OUT.write('    '.join(header_elements) + '\n')

# Get flagstat values for each sample
with open(concat_flagstat_file, 'r') as INPUT:
    sample_list = []
    for line in INPUT:
        # Get sample ID
        match = re.search('^# (.*)', line)
        if match:
            # Write previous sample list
            if sample_list:
                OUT.write('    '.join(sample_list) + '\n')

            # Get new sample ID
            file_path = match.group(1)
            file_name = file_path.split('/')[-1]
            chop_id = file_name.split('-')[1:]
            raw_filename = ''.join(chop_id)
            sample_id = raw_filename.split('.')[0]
            sample_list = [series, sample_id]
        else:
            # Get the first value of each line and store in list
            value = line.split()[0]
            sample_list.append(value)
    OUT.write('    '.join(sample_list) + '\n')
OUT.close()
            
