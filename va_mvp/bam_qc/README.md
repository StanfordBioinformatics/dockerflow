## BAM-QC Dockerflow - Ready

Dockerflow to perform preliminary QC checks on bam files provided by Bina as part of the VA MVP project.

### Dockerflow Files:

- bam-qc-workflow.yaml: Run FastQC and Samtools Flagstat on a set of bam files and generate summary plots.

- fastqc-task.yaml: Run FastQC on a bam file.

- plot-fastqc-task.yaml: Generate summary R plots from FastQC data.

- run-flagstat-task.yaml: Run Samtools Flagstat on bam file. 

- plot-flagstat-task.yaml: Generate summary R plots from Flagstat data.

- concatenate-files-task.yaml: Concatenate a list of files.

### Usage:
Test inputs:
```
dockerflow \
--project=your-project \
--workspace=gs://your-bucket/path/to/workspace/BamQC \
--workflow-file=bam-qc-workflow.yaml \
--inputs-from-file=input_bams=list_of_bam_file_gs_links.txt \
--inputs=series=arbitrary-name
--test
--runner=DirectPipelineRunner
```

Run:
```
dockerflow \
--project=your-project \
--workspace=gs://your-bucket/path/to/workspace/BamQC \
--workflow-file=bam-qc-workflow.yaml \
--inputs-from-file=input_bams=list_of_bam_file_gs_links.txt \
--inputs=series=arbitrary-name
```

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
docker tag plot_flagstat:1.0 gcr.io/your-project/plot_flagstat:1.0
gcloud docker push gcr.io/your-project/plot_flagstat:1.0
```

Test inputs:
```
dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://your-bucket/path/to/workspace/Flagstat \
--workflow-file=samtools-flagstat-workflow.yaml \
--inputs-fron-file=RunFlagstat.input_bam=list_of_bam_file_gs_links.txt \
--inputs=PlotFlagstat.series=arbitrary-name \
--test \
--runner=DirectPipelineRunner
```

Run:
```
dockerflow \
--project=your-project \
--workspace=gs://your-bucket/path/to/workspace/PlotFlagstat \
--workflow-file=samtools-flagstat-workflow.yaml \
--inputs-from-file=RunFlagstat.input_bam=list_of_bam_file_gs_links.txt \
--inputs=PlotFlagstat.series=arbitrary-name
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
--inputs-from-file=RunFastQC.input_bam=list_of_bam_file_gs_links.txt \
--inputs=PlotFastQC.series=arbitrary_name
```
