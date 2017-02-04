#!/usr/bin/env python

import re
import sys
import numpy

# Take file with concatenated flagstat results as input
concat_fastqc_file = sys.argv[1]
series = sys.argv[2]    # Arbitrary index for grouping samples in R ggplot
table_concat_fastqc_file = sys.argv[3]

# Create R formatted table file and add header
OUT = open(table_concat_fastqc_file, 'w')
header_elements = [
                   'series',
                   'sample',
                   'mean_base_quality',
                   'mean_seq_quality',
                   'average_gc_content',
                   'sequence_length']
OUT.write('    '.join(header_elements) + '\n')

# Get flagstat values for each sample
with open(concat_fastqc_file, 'r') as INPUT:
    record_seq_qual = False
    sample_list = []
    per_base_seq_qual_list = []
    for line in INPUT:
        # Get sample ID
        match_filename = re.search('# (.*)$', line)
        match_gc_content = re.search('\%GC\s+(\d+)', line)
        match_base_qual = re.search('#Base\s+Mean\s+Median', line)
        match_seq_len = re.search('^Sequence\s+length\s+(\d+)', line)
        match_seq_qual = re.search('^#Quality\s+Count')
        if match_filename:  # READY
            print 'Found filename'
            print line
            # Write previous sample list
            if sample_list:
                sample_list.append(str(mean_per_base_seq_qual))
                sample_list.append(mean_gc_content)
                sample_list.append(sequence_length)
                sample_list.extend(per_base_seq_qual_list)
                #print sample_list

                OUT.write('    '.join(sample_list) + '\n')

            mean_per_base_seq_qual = None
            mean_gc_content = None
            sequence_length = None
            per_base_seq_qual_list = []
            sample_list = []

            # Get new sample ID
            file_path = match_filename.group(1)
            file_name = file_path.split('/')[-1]
            chop_id = file_name.split('-')[1:]
            raw_filename = ''.join(chop_id)
            sample_id = raw_filename.split('.')[0]
            sample_list = [series, sample_id]
        
        elif match_gc_content: # READY
            print 'Found GC content'
            print line
            mean_gc_content = match_gc_content.group(1)

        elif match_seq_len:
            print 'Found seq len'
            print line
            sequence_length = match_seq_len.group(1)
        
        elif match_base_qual:    # READY
            print 'Found base quality start'
            print line
            record_base_qual = True

        elif record_base_qual:
            end_module_match = re.search('^>>END_MODULE', line)
            if end_module_match:
                record_base_qual = False
                mean_per_base_seq_qual = numpy.mean(list(map(float, per_base_seq_qual_list)))
            else:
                elements = line.split()
                mean_base_qual = str(elements[1])
                per_base_seq_qual_list.append(mean_base_qual)

        elif match_seq_qual:
            print 'Found sequence quality scores'
            print line
            record_seq_qual = True

        ''' IMPLEMENT THIS
        elif record_seq_qual:
            end_module_match = re.search('^>>END_MODULE', line)
            if end_module_match:
                record_base_qual = False
                mean_per_base_seq_qual = numpy.mean(list(map(float, per_base_seq_qual_list)))
            else:
                elements = line.split()
                mean_base_qual = str(elements[1])
                per_base_seq_qual_list.append(mean_base_qual)
        '''


    sample_list.append(str(mean_per_base_seq_qual))
    sample_list.append(mean_gc_content)
    sample_list.append(sequence_length)
    sample_list.extend(per_base_seq_qual_list)
    OUT.write('    '.join(sample_list) + '\n')
OUT.close()
            
