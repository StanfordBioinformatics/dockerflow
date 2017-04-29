#!/bin/bash

dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/FastQCBam \
--workflow-file=../workflow-fastqc-bam.yaml \
--inputs-fron-file=FastQCBam.input_bam=../test_inputs/input_bams.txt \
--inputs=Text2Table.series=test,\
#Text2Table.sample_index=6,\
Text2Table.schema=fastqc,\
ConcatenateFiles.concat_file=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/FastQCBam/bam_fastqc_concat.csv \
#--test \
#--runner=DirectPipelineRunner