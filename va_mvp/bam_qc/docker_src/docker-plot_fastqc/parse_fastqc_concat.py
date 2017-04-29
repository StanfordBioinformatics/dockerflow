#!/usr/bin/env python

import re
import sys

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

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
                   'sequence_length',
                   '1',
                   '2',
                   '3',
                   '4',
                   '5',
                   '6',
                   '7',
                   '8',
                   '9',
                   '10-11',
                   '12-13',
                   '14-15',
                   '16-17',
                   '18-19',
                   '20-21',
                   '22-23',
                   '24-25',
                   '26-27',
                   '28-29',
                   '30-31',
                   '32-33',
                   '34-35',
                   '36-37',
                   '38-39',
                   '40-41',
                   '42-43',
                   '44-45',
                   '46-47',
                   '48-49',
                   '50-51',
                   '52-53',
                   '54-55',
                   '56-57',
                   '58-59',
                   '60-61',
                   '62-63',
                   '64-65',
                   '66-67',
                   '68-69',
                   '70-71',
                   '72-73',
                   '74-75',
                   '76-77',
                   '78-79',
                   '80-81',
                   '82-83',
                   '84-85',
                   '86-87',
                   '88-89',
                   '90-91',
                   '92-93',
                   '94-95',
                   '96-97',
                   '98-99',
                   '100-101']
OUT.write('    '.join(header_elements) + '\n')

# Get flagstat values for each sample
with open(concat_fastqc_file, 'r') as INPUT:
    record_base_qual = False
    record_seq_qual = False
    sample_list = []
    per_base_seq_qual_list = []
    for line in INPUT:
        # Get sample ID
        match_filename = re.search('# (.*)$', line)
        match_gc_content = re.search('\%GC\s+(\d+)', line)
        match_base_qual = re.search('#Base\s+Mean\s+Median', line)
        match_seq_len = re.search('^Sequence\s+length\s+(\d+)', line)
        match_seq_qual = re.search('^#Quality\s+Count', line)
        if match_filename:  # READY
            print 'Found filename'
            print line
            # Write previous sample list
            if sample_list:
                sample_list.append(str(mean_per_base_seq_qual))
                sample_list.append(str(mean_seq_qual))
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
                mean_per_base_seq_qual = mean(list(map(float, per_base_seq_qual_list)))
                #mean_per_base_seq_qual = numpy.mean(list(map(float, per_base_seq_qual_list)))
            else:
                elements = line.split()
                mean_base_qual = str(elements[1])
                per_base_seq_qual_list.append(mean_base_qual)

        elif match_seq_qual:
            print 'Found sequence quality scores'
            print line
            record_seq_qual = True
            total_seq_count = 0
            total_seq_quality = 0

        elif record_seq_qual:
            end_module_match = re.search('^>>END_MODULE', line)
            if end_module_match:
                record_seq_qual = False
                mean_seq_qual = float(total_seq_quality) / float(total_seq_count)
            else:
                elements = line.split()
                quality = elements[0]
                count = elements[1]

                quality_sum = float(quality) * float(count)

                total_seq_count += float(count)
                total_seq_quality += quality_sum

                print ('# ' + str(total_seq_count))
                print ('## ' + str(total_seq_quality))


    sample_list.append(str(mean_per_base_seq_qual))
    sample_list.append(str(mean_seq_qual))
    sample_list.append(mean_gc_content)
    sample_list.append(sequence_length)
    sample_list.extend(per_base_seq_qual_list)
    OUT.write('    '.join(sample_list) + '\n')
OUT.close()
            
