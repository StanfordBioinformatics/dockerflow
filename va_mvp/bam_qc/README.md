## BAM-QC Dockerflow - *Under Construction*

Dockerflow to perform preliminary QC checks on bam files provided by Bina as part of the VA MVP project.

### Files:

- bam-qc-workflow.yaml: Workflow file describing all steps involved in bam-qc process.

- bam-qc-args.yaml: File containing arguments passed to bam-qc workflow.

- fastqc-task.yaml: Task file to run FastQC on bam file.

- samtools-flagstat-task.yaml: Task file to run Samtools Flagstat on bam file. 

## Samtools Flagstat Dockerflow - Ready

Dockerflow for running Samtools Flagstat on a list of bam files, concatenating the outputs, and generating summary R plots.

### Files:

- **samtools-flagstat-workflow.yaml**: Workflow file.

- **run-flagstat-task.yaml**: Task file; run Samtools Flagstat.

- **concatenate-files-task.yaml**: Task file; concatenate flagstat output files.

- **plot-flagstat-task.yaml**: Task file; use python script to parse output into R-readable table format. Use R script to generate plots.

### Usage:
Create Docker image:
```
cd plot_flagstat_docker
docker build -t plot_flagstat:1.0 .
docker tag plot_flagstat:1.0 gcr.io/gbsc-gcp-project-mvp/plot_flagstat:1.0
gcloud docker push gcr.io/gbsc-gcp-project-mvp/plot_flagstat:1.0
```

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
--inputs-from-file=RunFlagstat.input_bam=test_inputs/phase2_bams.txt \
--inputs=PlotFlagstat.series=Bina_170201
```

## FastQC Dockerflow - Ready

### Files:

- **fastqc-workflow.yaml**: Workflow file.

- **run-fastqc-task.yaml**: Run FastQC on a bam file and output fastqc.zip, fastqc.html, and fastqc_data.txt files.

- **concatenate-files-task.yaml**: Concatenate all fastqc_data.txt files.

- **plot-fastqc-task.yaml**: Use Python script to convert concatenated fastqc_data file into table format. Use R script to generate boxplots describing mean base quality, mean sequence quality, and average GC content. Scripts are in plot_fastqc_docker/.

### Usage:
Create Docker image:  
See Flagstat section.

Test inputs:  
See Flagstat section.

Run:
```
dockerflow \
--project=your-project-name \
--workspace=gs://your-bucket-name/path/to/arbitrary/workspace \
--workflow-file=fastqc-workflow.yaml \
--inputs-from-file=RunFastQC.input_bam=file_with_list_of_gs_bam_file_links.txt \
--inputs=PlotFastQC.series=arbitrary_name
```
