#!/bin/bash

dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/Flagstat \
--workflow-file=../workflow-flagstat.yaml \
--inputs-fron-file=RunFlagstat.input_bam=../test_inputs/input_bams.txt \
--inputs=Text2Table.series=test,\
#Text2Table.sample_index=6,\
Text2Table.schema=flagstat,\
ConcatenateFiles.concat_file=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/Flagstat/flagstat_concat.csv \
#--test \
#--runner=DirectPipelineRunner