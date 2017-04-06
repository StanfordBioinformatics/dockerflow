#!/usr/bin/env python
'''
Description: Convert results from a *fastqc_data.txt file into table format.
'''

__author__ = 'pbilling@stanford.edu (Paul Billing-Ross)'

import re
import pdb
import sys
import json

'''
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

# Take file with concatenated flagstat results as input
fastqc_file = sys.argv[1]
series = sys.argv[2]    # Arbitrary index for grouping samples in R ggplot
sample_name = sys.argv[3]
csv_fastqc_file = '{}_fastqc_data.csv'.format(sample_name)

# Create R formatted table file and add header
OUT = open(table_concat_fastqc_file, 'w')
# Don't actually write the header
'''
'''
header_elements = [
                   'series',
                   'sample',
                   'basic_stats',
                   'poor_qual_sequences',
                   'sequence_length',
                   'gc_content',
                   'base_index',
                   'mean_per_base_quality',
                   'median_per_base_quality']
OUT.write('    '.join(header_elements) + '\n')
'''

''' new
header_elements = [
                   'series',
                   'sample',
                   'dimension',
                   'index',
                   'value']
'''
'''
# Get flagstat values for each sample
sample_list = []
sample_list.append(series)
sample_list.append(sample_id)

basic_stats = None


with open(fastqc_file, 'r') as INPUT:
    record_base_qual = False
    record_seq_qual = False
    sample_list = []
    per_base_seq_qual_list = []
    for line in INPUT:
        # Get sample ID
        #match_filename = re.search('# (.*)$', line)
        match_basic_stats = re.match('>>Basic Statistics\t(?P<basic_stats>\w+)', line)
        match_gc_content = re.match('\%GC\s+(?P<gc_content>\d+)', line)
        match_base_qual = re.match('#Base\s+Mean\s+(?P<per_base_qual>Median)', line)
        match_seq_len = re.match('Sequence\s+length\s+(?P<seq_len>\d+)', line)
        match_seq_qual = re.match('#Quality\s+(?P<seq_quality>Count)', line)

        # Get the true match
        match_list = [
                      match_basic_stats,
                      match_gc_content,
                      match_base_qual,
                      match_seq_len,
                      match_seq_qual]
        true_matches = ifilter(lambda x: x > 0, match_list)
        true_match = true_matches.next()
        dimension = true_match.groupdict.keys()[0]
        value = true_match.groupdict.values()[0]
        
        try:
            true_matches.next()
            "More than 1 match"
            sys.exit()
        except:
            continue

        # Execute the logic to do the thing with the match

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
    
        elif match_gc_content:
            print 'Found GC content'
            print line
            mean_gc_content = match_gc_content.group(1)

        elif match_seq_len:
            print 'Found seq len'
            print line
            sequence_length = match_seq_len.group(1)
        
        elif match_base_qual:
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

OUT.close()
'''
            

# I want a generalizable framework for converting text -> table
# What if I write table parser as a class and abstract away the matches.
# Include matches as an argument?

class FlexTableParser:

    def __init__(schema_file, static_values={}, out_fh):
        
        self.static_values = static_values
        self.output_file = output_file

        with open(config_file, 'r') as config_fh:
            self.config = json.load(config_fh)
        self.schema = self.config['schema']
        self.dimensions = self.config['dimensions']

        self.match_patterns = []
        for dimension in dimensions:
            regex_pattern = dimension['regex_pattern']
            self.match_patterns.append(regex_pattern)

    def _write_single_row(self, dimension, value, out_fh):
        '''Write single row to table.

        Args:
            dimension (str):
            value (int/float): 

        '''

        # Fixed at 1 when writing single row
        index = 1
        
        # Combine line-entry values with static values
        table_values = {
                        'dimension': dimension,
                        'index': index,
                        'value': value
                       }
        static_values = self.static_values.copy()
        table_values.update(static_values)

        # Populate out string ordered by schema
        strings = [str(table_values[column]) for column in schema]
        out_str = ','.join(strings) + '\n'
        output_fh.write(out_str)

    def _write_series_rows(self, dimension, in_fh, out_fh):
        '''Write series of rows.
        '''

        # Indexes of the delimiter separated line.
        # (I know, I know... need better terminology.)
        index_element = dimension['index']  # type: int
        value_element = dimension['value']  # type: int

        delimiter = dimension['delimiter'] # type: str
        stop_pattern = dimension['stop_pattern'] # type: str

        stop = False

        while stop == False:
            table_values = self.static_values.copy()
            line = in_fh.next()
            stop_match = re.match(stop_pattern, line)
            if stop_match:
                stop = True
            else:
                elements = line.split(delimiter)
                table_values['dimension'] = dimension['name']
                table_values['index'] = elements[index_element]
                table_values['value'] = elements[value_element]

                # Convert all values to schema ordered strings
                strings = [str(table_values[column]) for column in schema]
                out_str = ','.join(strings) + '\n'
                out_fh.write(out_str)

    def parse_file(self, in_file, out_fh):
        with open(input_file, 'r') as input_fh:
            for line in input_fh:
                matches = [re.match(regex, line) for regex in self.match_patterns]
                true_matches = list(ifilter(lambda x: x > 0, matches))
                if len(true_matches) == 0:
                    continue
                elif len(true_matches) > 1:
                    print 'Error: Multiple regex patterns matched this line.'
                    print line
                    pdb.set_trace()
                elif len(true_matches) == 1:
                    true_match = true_matches[0]
                    dimension_name = true_match.groupdict().keys()[0]
                    row_type = self.dimensions[dimension_name]['row_type']
                    if dimenstion_type == 'single':
                        value = true_match.groupdict().values()[0]
                        self._write_single_row(dimension_name, value, out_fh)
                    elif dimension_Type == 'series':
                        dimension = self.dimensions[dimension_name]
                        self._write_series_row(dimension, in_fh, out_fh)
                    else:
                        print 'Error: Invalid dimension type: {}'.format(dimension_type)
                        pdb.set_trace()


# If type is single, value is automatically groupdict()[dimension] and index = 1.
# If type is series, value_index and value are indexes of string elements separated by delimiter. 


def main():

    schema_file = 'table_conversion_schema.json'

    series = 'test'
    sample = 'sampleA'
    input_file = 'alignments_fastqc_data.txt'
    output_file = 'alignments_fastqc_table.csv'

    static_values = {
                    'series': 'test',
                    'sample': 'sampleA'
                   }

    out_file = 'flex_table_parser_out.txt'
    out_fh = open(out_file, 'a')
    in_file = '/Users/pbilling/Documents/GitHub/dockerflow/va_mvp/bam_qc/test_inputs/alignments_fastqc_data.txt'
    in_fh = open(in_file, 'r')

    table_parser = FlexTableParser(schema_file, static_values)  
    table_parser.parse_file(in_file, out_fh)

if __name__ == '__main__':
    main()


'''
    def main():

        self.in_fh = open(self.input_file, 'r')
        self.out_fh = open(self.output_file, 'w')

        for line in in_fh:
            get_match()
        
        matches = [
                   re.match('>>Basic Statistics\t(?P<basic_stats>\w+)', line)
                   re.match('\%GC\s+(?P<gc_content>\d+)', line)
                   re.match('#Base\s+Mean\s+(?P<per_base_qual>Median)', line)
                   re.match('Sequence\s+length\s+(?P<seq_len>\d+)', line)
                   re.match('#Quality\s+(?P<seq_quality>Count)', line)]

        true_matches = ifilter(lambda x: x > 0, match_list)
        true_match = true_matches.next()
        
        self.dimension = true_match.groupdict.keys()[0]
        self.value = true_match.groupdict.values()[0]
        
        try:
            true_matches.next()
            "More than 1 match"
            sys.exit()
        except:
            continue
'''


