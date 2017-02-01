##BAM-QC Dockerflow - Under Construction

Dockerflow to perform preliminary QC checks on bam files provided by Bina as part of the VA MVP project.

###Files:

- bam-qc-workflow.yaml: Workflow file describing all steps involved in bam-qc process.

- bam-qc-args.yaml: File containing arguments passed to bam-qc workflow.

- fastqc-task.yaml: Task file to run FastQC on bam file.

- samtools-flagstat-task.yaml: Task file to run Samtools Flagstat on bam file. 

##Samtools Flagstat Dockerflow - Ready

Dockerflow for running Samtools Flagstat on a list of bam files, concatenating the outputs, and generating summary R plots.

###Files:

- samtools-flagstat-workflow.yaml: Workflow file.

- run-flagstat-task.yaml: Task file; run Samtools Flagstat.

- concatenate-files-task.yaml: Task file; concatenate flagstat output files.

- plot-flagstat-task.yaml: Task file; use python script to parse output into R-readable table format. Use R script to generate plots.

###Usage:
Test inputs:
```
dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/PlotFlagstat \
--workflow-file=samtools-flagstat-workflow.yaml \
--inputs-fron-file=RunFlagstat.input_bam=test_inputs/phase2_bams.txt \
--inputs=PlotFlagstat.series=Bina_170201 \
--test \
--runner=DirectPipelineRunner
```

Run:
```
dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/bam_qc/PlotFlagstat \
--workflow-file=samtools-flagstat-workflow.yaml \
--inputs-fron-file=RunFlagstat.input_bam=test_inputs/phase2_bams.txt \
--inputs=PlotFlagstat.series=Bina_170201
```
