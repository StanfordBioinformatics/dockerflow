#!/bin/bash

dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/Vcfstats \
--workflow-file=../workflow-rtg-vcfstats.yaml \
--inputs-fron-file=RunRtgVcfstats.vcf_gz=../test_inputs/gs_bina_vcfs_10.txt \
--inputs=Text2Table.series=test,\
ConcatenateFiles.concat_file=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/Vcfstats/vcfstats_concat.csv \
#--test \
#--runner=DirectPipelineRunner
