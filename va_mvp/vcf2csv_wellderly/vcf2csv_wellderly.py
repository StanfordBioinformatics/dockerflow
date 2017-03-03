#!/usr/bin/env python
# version: 0.2

''' Changes from vcf2csv_wellderly:
    Added frequency metrics to match those reported in Wellderly paper.
    Added variant_type from VCF file

'''

import os
import re
import sys
import glob
import gzip
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_vcf', dest='input_vcf_gz', required=True)
    #parser.add_argument('-p', '--input_pattern', dest='pattern', required=True)
    parser.add_argument('-o', '--output_csv', dest='output_csv', required=True)
    args = parser.parse_args()


    #vcf_fh = gzip.open(args.input_vcf_gz, 'r')
    out_fh = open(args.output_csv, 'w')

    # reference_name start END reference_bases alternate_bases allele_frequency 
    #out_fh.write('reference_name,start,END,reference_bases,alternate_bases,allele_frequency,allele_count,frequency_type\n')

    # Find all matching files
    #for vcf_file in glob.glob(args.pattern):
    #    vcf_fh = gzip.open(vcf_file, 'r')

    # illumina columns: #CHROM POS ID REF ALT QUAL FILTER INFO
    # cg columns:       #CHROM POS ID REF ALT QUAL FILTER INFO

    vcf_fh = gzip.open(args.input_vcf_gz, 'r')
    for line in vcf_fh:

        comment = re.search('^#', line)
        if comment:
            #out_fh.write(line)
            continue

        fields = line.split('\t')
        ref_name = fields[0]
        start = str(int(fields[1]) - 1)
        end = str(int(fields[1]))
        ref_bases = fields[3]
        alt_bases = fields[4]
        # Determine whether there are multiple altenate bases
        alt_bases = fields[4].split(',')
        #if len(alt_bases) > 1:
        
        alt_base_data = {} # alt_base_data[base] = [frequency, count]
        for base in alt_bases:
            alt_base_data[base] = []
        info = fields[7]
        elements = info.split(';')
        if len(elements) != 11:
            print len(elements)
            print info
            print line
            continue
        variant_type = elements[0]
        allele_freq = elements[7]
        allele_count = elements[8]

        allele_counts = allele_count.split(',')
        allele_freqs = allele_freq.split(',')

        allele_count_dict = {}
        allele_freq_dict = {}

        for element in allele_counts:
            dash_match = re.search('^--(.*)', element)
            if dash_match:
                #elements = element.split('-')
                allele = '-'
                count = dash_match.group(1)
            else:
                elements = element.split('-')
                allele = elements[0]
                count = elements[1]
            allele_count_dict[allele] = count

        for element in allele_freqs:
            elements = element.split('-')
            dash_match = re.search('^--(.*)', element)
            if dash_match:
                #elements = element.split('-')
                allele = '-'
                count = dash_match.group(1)
            else:
                elements = element.split('-')
                allele = elements[0]
                freq = elements[1]
            allele_freq_dict[allele] = freq

        for alt_base in alt_base_data:
            try:
                allele_freq = float(allele_freq_dict[alt_base])
                allele_count = int(allele_count_dict[alt_base])
            except:
                print line
                print alt_base_data
                sys.exit()

            # Categorize by AAA allele freq criteria [common,low,rare,singleton,none]
            aaa_freq_category = None
            if allele_count > 1:
                if float(allele_freq) >= 0.05:
                    aaa_freq_category = 'common'
                elif float(allele_freq) >= 0.005 and float(allele_freq) < 0.05:
                    aaa_freq_category = 'low'
                elif float(allele_freq) < 0.005:
                    aaa_freq_category = 'rare'
            elif allele_count == 1:
                aaa_freq_category = 'singleton'
            else:
                aaa_freq_category = 'absent'

            # Categorize by Scripps allele freq criteria [rare, uncommon, common]
            scripps_freq_category = None
            if allele_count >= 1:
                if float(allele_freq) > 0.05:
                    scripps_freq_category = 'common'
                elif float(allele_freq) >= 0.01 and float(allele_freq) <= 0.05:
                    scripps_freq_category = 'uncommon'
                elif float(allele_freq) < 0.01:
                    scripps_freq_category = 'rare'
            else:
                scripps_freq_category = 'absent' 

            csv_elements = [
                            ref_name,
                            start,
                            end,
                            ref_bases,
                            alt_base,
                            variant_type,
                            str(allele_freq),
                            str(allele_count),
                            aaa_freq_category,
                            scripps_freq_category]
            csv_out = ','.join(csv_elements) + '\n'
            out_fh.write(csv_out)

    vcf_fh.close()
    out_fh.close()

if __name__ == '__main__':
    main()
