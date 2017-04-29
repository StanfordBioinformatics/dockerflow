#!/bin/bash

dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/FastQCBina \
--workflow-file=../workflow-text2table-concat.yaml \
--inputs-fron-file=Text2Table.input_file=../test_inputs/gs_bina_fastqc_170404_10.txt \
--inputs=Text2Table.series=test,\
#Text2Table.sample_index=6,\
Text2Table.schema=fastqc,\
ConcatenateFiles.concat_file=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/FastQCBina/bina_fastqc_concat.csv \
#--test \
#--runner=DirectPipelineRunner