**BAM-QC Dockerflow**

Dockerflow to perform preliminary QC checks on bam files provided by Bina as part of the VA MVP project.

Files:

- bam-qc-workflow.yaml: Workflow file describing all steps involved in bam-qc process.

- bam-qc-args.yaml: File containing arguments passed to bam-qc workflow.

- fastqc-task.yaml: Task file to run FastQC on bam file.

- samtools-flagstat-task.yaml: Task file to run Samtools Flagstat on bam file. 
