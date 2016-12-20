# Guide to building a structural variant caller Dockerflow

## Disclaimer
Dockerflow is not an official Google product. This is not an official guide nor was it written by a Googler.

## Overview
This guide is designed to demonstrate effective practices for building Dockerflows to run workflows through Dataflow on the Google Cloud Platform.

## Outline
- [Dictionary](#dictionary)
- [Install Dockerflow](#install-dockerflow)
- [Write basic workflow file](#base-workflow)
- [Add task structure](#design-workflow)
- [Write basic task file](#base-task)
- [Build Docker image for task](#build-docker)
- [Upload test files to Cloud Storage](#upload-test-files)
- [Update task file](#update-task)
- [Choose a file management pattern](#file-management)
- [Commit Docker image to GCP](#commit-docker)
- [Create args file](#create-args")
- [Perform workflow dry-run](#run-test)
- [Test workflow locally](#run-locally)
- [Test workflow on GCP](#run-gcp)
- [Rinse & repeat](#repeat)
- [Bonus: Check if docker image already exists for task](#biocontainers)

## <a name="dictionary"></a>Dictionary
- Task: A task describes a single operation in a workflow. Each task is associated with a YAML task file, a Docker image, and a set of inputs and outputs.
- Workflow: A workflow is the orientation of a set of tasks to obtain a set of outputs. A workflow is described in a YAML file with descriptions of all tasks as well as the the orientation they are to be run.
- GCP: Google Cloud Platform
- GCS: Google Cloud Storage

## <a name="install-dockerflow"></a>Install Dockerflow
Instructions for installing Dockerflow can be found on the main page of the repo: https://github.com/googlegenomics/dockerflow

## <a name="base-workflow"></a>Write base workflow file

Now that we know the tasks involved in our workflow and the structure of the workflow, we can draft a workflow document. This will serve as an outline as we build our Dockerflow.

```
version: v1alpha2
defn:
  name: SV_Caller
  description: Use multiple bioinformatics tools to call genomics structural variants.

steps: 
- defn:
    name: Pindel
  defnFile: pindel-task.yaml
- defn:
    name: Breakdancer
  defnFile: breakdancer-task.yaml
- defn:
   name: CNVnator
  defnFile: cnvnator-task.yaml
- defn:
    name: BreakSeq
  defnFile: breakseq-task.yaml
```

The first task I am going to add is Pindel, so for now I will comment out all the other branches and task definitions.

```
version: v1alpha2
defn:
  name: SV_Caller
  description: Use multiple bioinformatics tools to call genomics structural variants.

graph:
- BRANCH:
  - Pindel
#  - Breakdancer
#  - CNVnator
#  - BreakSeq

steps: 
- defn:
    name: Pindel
  defnFile: pindel-task.yaml
#- defn:
#    name: Breakdancer
#  defnFile: breakdancer-task.yaml
#- defn:
#   name: CNVnator
#  defnFile: cnvnator-task.yaml
#- defn:
#    name: BreakSeq
#  defnFile: breakseq-task.yaml
args:
  inputs:
```

## <a name="design-workflow"></a>Design workflow tasks structure

**Pattern 1**: If you want to run all tasks serially, you do not need to describe any branching pattern and can leave the branching section out of your workflow file.

**Pattern 2**: Run all tasks in parallel
```
- BRANCH:
  - Breakdancer
  - CNVnator
  - BreakSeq
  - Pindel
```

**Pattern 3**: Can run multiple tasks serially in one branch, while running another task in parallel on a different branch

```
- BRANCH:
  -- Breakdancer
   - CNVnator
   - BreakSeq
  - Pindel
```

We will use pattern 2 to run all tasks in parallel, since none of our tasks rely on output from other tasks.

## <a name="base-task"></a>Write base Dockerflow task file

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:

outputParameters:

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.0'
  cmd: |
```

This is the current draft of 'pindel-task.yaml', the Pindel task file. The task file describes everything involved in executing the Pindel task. This includes inputs, outputs, and the commands that will be run in the Pindel docker image. Currently it only has values for the name, description, and docker:imageName.  As we figure out more about running Pindel, we can fill in these values.

The docker image is named gcr.io/your_project_name/task_name. We haven't created the docker image yet, but I already have enough information to infer what it will be named. Once I know more about how breakdancer works, I can fill in the sections for input/output parameters and the command to be run in docker.

## <a name="build-docker"></a>Build the Docker image
Docker images are the engines that perform all the operations in Dockerflow. Each task in our dockerflow will be associated with a docker image and each image can be customized with executables and scripts specially designed to carry out that task.

We will be borrowing from the inimtable Greg McInnes's Pipelines API Demo to learn how to build docker images. You can also check out his demo here: https://github.com/StanfordBioinformatics/pipelines-api-examples/tree/master/demo 

### Launching a Docker Container
First, check that Docker is running on your machine.

```
$ docker help
```

Now try downloading a Docker image containing a basic Ubuntu OS.

```
$ docker pull ubuntu
```

Launch an interactive Docker container from the ubuntu Docker image. A Docker container is a live instance of a Docker image and represents its own computing environment.

```
$ docker run -ti ubuntu /bin/bash
```

If this runs successfully your command prompt should now look something like this:
```
root@589558b93b5a:/#
``` 
Congratulations, you are now working inside a Docker container!

### Structuring Docker images
When building a Docker image, we want to keep it install the minimum number of tools required to perform the specific task we are working on. This will allow us to keep each Docker image small and avoid any compatibility issues between different softwares and dependencies.

Since we want to run four different tools, we will likely be using four different Docker images; each one specifically configured for each task. However, there are common utilities that we will likely use in all our Docker images. Because of this, we are going to first create a Docker image with some common utilities, and then use that as the base to make each of our other task-specific images.

### Add tools to the Docker container

The 'ubuntu' image we are using has only the bare bones of the Ubuntu OS. In order to get, install, and run our bioinformatics software we are going to need to get additional utilities.

We can try inferring which utilities we'll need by looking at the download & install instructions for each of the tools we intend to use. We probably won't be able to infer all of them, especially for software that has to be compiled from source. That's fine; when we run into these we'll just have to decide whether it's appropriate to go back and add those resources to our base ubuntu image or install them on an image-by-image basis for each task. 

From previous experience and by looking at the dependencies for our software packages, I'm going to install the following utlities and libraries.

Install general utilities
```
# apt-get update
# apt-get install wget
# apt-get install curl
# apt-get install vim
# apt-get install unzip
# apt-get install git  
```

Install tools required for samtools
```
# apt-get install tar
# apt-get install bzip2
# apt-get install make
# apt-get install gcc
# apt-get install libncurses5-dev
# apt-get install zlib1g-dev
```

Install tools required for pindel
```
# apt-get install g++
```

Install gsutil (discussed later)
```
# apt-get install curl
# apt-get install lsb-release
# export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
# echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list
# curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
# apt-get update && apt-get install google-cloud-sdk
# gcloud init
```

With these basic tools installed, exit the container and commit it to a new Docker image.

```
# root@bca9ac41b690:/# exit
$ docker commit -m "Ubuntu with utilities" -a "pbilling" bca9ac41b690 sv_caller_base:1.0
sha256:3b6cc05a3156981914249a610b871c36e2dcd762fb3e561616ed3a6810db8e8f
```

Now let's launch a new container of our newly created sv_caller_base:1.0 image and install Pindel.

```
$ docker run -ti sv_caller_base:1.0
```

Pindel requires the htslib library as a pre-req, so we'll need to install it: http://www.htslib.org/download/

```
# mkdir /usr/local/software
# wget https://github.com/samtools/htslib/releases/download/1.3.2/htslib-1.3.2.tar.bz2
# tar xvfj htslib-1.3.2.tar.bz2 
# ./configure
# make
# make install
# exit
```

And now let's install Pindel.

```
# cd /usr/local/software
# git clone git://github.com/genome/pindel.git
# cd pindel
# ./INSTALL ../htslib-1.3.3
```

Run Pindel in the Docker container to verify that it has been installed properly.

```
# cd demo
# ../pindel -i simulated_config.txt -f simulated_reference.fa -o bamtest -c ALL
``` 

## <a name="upload-test-files"></a>Upload test files to Google Cloud storage
We've verified that Pindel has been successfully installed in our Docker container, but before we commit our container to an image, let's upload some of the Pindel demo files to Google Cloud Storage. These will be useful for testing our Pindel Dockerflow task.

```
# gsutil cp simulated_* gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel
```
## <a name="update-task"></a>Update task file 
With Pindel installed in our container, we can start filling in the Pindel task file. First, we need to figure out how to run Pindel. The Pindel authors have conveniently provided a RUNME script that will give us an idea of common use-cases and arguments. We can also read the documentation. And now let's add those to the Pindel task file.

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:
- name: input_bam
  type: file[]
- name: bam_config_file
  type: file
- name: reference_fasta
  type: file
- name: output_prefix
- name: name_of_chromosome
- name: reference_name
- name: reference_date

outputParameters:
 - name: output_vcf
   defaultValue: ${output_prefix}.vcf
   type: file
 

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.0'
  cmd: |
    export PATH=$PATH:/usr/local/software/pindel
    pindel -i ${bam_config_file} -f ${reference_fasta} -o ${output_prefix} -c ${name_of_chromosome}
    pindel2vcf -P ${output_prefix} -r ${reference_fasta} -R ${reference_name} -d ${reference_date}
```

### inputParameters
Because we may have multiple bam files, we use "type: file[]" to specify that "input_bam" represents a list of files instead of just a single one. I am only specifying one file for "bam_config_file" and "reference_fasta", so those are of "type: file".

### outputParameters
In the "outputParameters" section, I have specified one file for output. Once all docker commands are complete Dockerflow will look for a file  matching this name and try to upload it the the workspace we have specified in Google Cloud Storage.

### docker:cmd
Here we use the pipe operator "|" to specify a list of commands that will be run serially, in our docker container. First we add the path of the Pindel executable to the environment variable "PATH" so that we can run Pindel from the command-line using only the name of the executable, "pindel". The following two commands will run "pindel" and then "pindel2vcf" to generate our output VCF file.

Unfortunately, **these commands will not work.** The reason for this will be discussed in the next section.

## <a name="file-management"></a>Choose a file management pattern
There are multiple methods you can use to handle file management in Dockerflow. The first is to use the native Dockerflow method. This is the easiest and most elegant solution; however, because of the way it tags files, it is not optimal for all cases. **Files managed by Dockerflow have an arbitrary numerical identifier appended to the beginning of all filenames.** Further description of this behavior can be found in the second comment of this issue: https://github.com/googlegenomics/dockerflow/issues/16. 

In cases where all input and output filenames are specified through by Dockerflow variables, this should be fine because Dockerflow knows to look for filenames with these appended IDs. However, if you are not explicity specifying all input and output filenames with Dockerflow input/output parameters, you will likely run into problems. Let's look at some examples demonstrating this behavior...

### Using the native method for managing Dockerflow files
```
# Mark duplicate reads to avoid counting non-independent observations
- defn:
    name: "MarkDuplicates"
    inputParameters:
    - name: "input_bams"
      type: "file[]"
      inputBinding:
        itemSeparator: " INPUT="
    - name: "output_bam_basename"
    - name: "metrics_filename"
    outputParameters:
    - name: "output_bam"
      defaultValue: "${output_bam_basename}.bam"
      type: file
    - name: "duplicate_metrics"
      defaultValue: "${metrics_filename}"
      type: file
    resources:
      minimumRamGb: "7"
      preemptible: true
    docker:
      imageName: "broadinstitute/genomes-in-the-cloud:2.2.3-1469027018"
      cmd: |
        java -Xmx4000m -jar /usr/gitc/picard.jar \
          MarkDuplicates \
          INPUT=${input_bams} \
          OUTPUT=${output_bam} \
          METRICS_FILE=${duplicate_metrics} \
          VALIDATION_STRINGENCY=SILENT \
          OPTICAL_DUPLICATE_PIXEL_DISTANCE=2500 \
          ASSUME_SORT_ORDER="queryname" \
          CREATE_MD5_FILE=true
```

This is an example "MarkDuplicates" task from the "gatk-workflow.yaml" example provided with Dockerflow. In this case, there is one set of inputs files, "input_bams", and two output files, "output_bam" and "duplicate_metrics". The filenames for all input and output files needed to run MarkDuplicates are explicity passed to MarkDuplicates through Dockerflow variables. At runtime, Dockerflow will automatically append the appropriate numerical ID to the filenames of the input files, run the task, find the output files with the same appended IDs, and then upload them back to GCS, while removing the IDs. If all goes well, the user never has to know about them.

Now let's look at an example using the native Dockerflow method for managing Pindel files:

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:
- name: input_bams
  type: file[]
- name: input_bais
  type: file[]
- name: bam_config_file
  type: file
- name: reference_fasta
  type: file
- name: reference_fai
  type: file
- name: output_prefix
- name: name_of_chromosome
- name: reference_name
- name: reference_date

outputParameters:
- name: output_vcf
  defaultValue: ${output_prefix}.vcf
  type: file

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.0'
  cmd: |
    export PATH=$PATH:/usr/local/software/pindel
    pindel -i ${bam_config_file} -f ${reference_fasta} -o ${output_prefix} -c ${name_of_chromosome}
    pindel2vcf -P ${output_prefix} -r ${reference_fasta} -R ${reference_name} -d ${reference_date} -v ${output_vcf}
```

This doesn't work. Why not?

Pindel takes, as input, a bam_config_file that is a text file with three columns specifying the bam name, insert size, and sample label. The sample config file for the Pindel demo looks like this:

```
simulated_sample_1.bam	250	SAMPLE1
simulated_sample_2.bam	250	SAMPLE2
simulated_sample_3.bam	250	SAMPLE3
```

However, if I pass this file as input to my Dockerflow Pindel task, it will fail. Pindel will be looking for files named "simulated_sample_N.bam", but the files on the datadisk will be named "NNNNNNNNNN-simulated_sample_N.bam" where the "N"s represent arbitratry integers. 

To get this to work, I need to know the specific ID that will be attached to the files in order to specify the filenames in the config file. Because, I can't know this before runtime, I would have to create the config file as part of the commands I run in the Dockerflow task. This is doable, but would probably involve obtuse bash commands that I don't know, and am not interested in learning. 

### Using gsutil to manage Dockerflow files

Gsutil is "a python application that let's you access Cloud Storage from the command line" (https://cloud.google.com/storage/docs/gsutil). Instead of having Dockerflow manage files for us, we can do it ourselves, using gsutil. This is a less elegant solution that does not really fit within the Dockerflow schema, but is does afford us more freedom in file handling.

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:
- name: input_bams_dir
- name: bam_config_file
- name: reference_fasta
- name: reference_fai
- name: output_prefix
- name: name_of_chromosome
- name: reference_name
- name: reference_date
- name: output_vcf

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.01'
  cmd: |
    export PATH=$PATH:/usr/local/software/pindel
    cd /mnt/data
    gsutil cp -r ${input_bams_dir}/*.bam .
    gsutil cp -r ${input_bams_dir}/*.bai .
    gsutil cp ${bam_config_file} .
    gsutil cp ${reference_fasta} .
    gsutil cp ${reference_fai} .
    pindel -i `basename ${bam_config_file}` -f `basename ${reference_fasta}` -o ${output_prefix} -c ${name_of_chromosome}
    pindel2vcf -P ${output_prefix} -r `basename ${reference_fasta}` -R ${reference_name} -d ${reference_date}
    gsutil cp ${output_prefix}.vcf ${output_vcf}
```

In using gsutil, we take responsibility from Dockerflow in specifying which variables represent files and how they should be handled. All inputs as passed as strings, so its up to us to keep track of which are files and how to process them. Instead of specifying each bam file individually, I passed a bam directory to the task and had it download all the *.bam/*.bai files in that directory. For input files that are passed to pindel we also have to take the additional step of removing the preceding gs:// path.

In forsaking the native Dockerflow form we gain freedom as well as variability and the opportunities for errors. Alternatively, we could take a hybrid approach by adding processing steps to chop off the IDs after they have been transferred to our datadisk. Something like this...

### Using a hybrid approach to managing Dockerflow files

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:
- name: input_bams
  type: file[]
- name: input_bais
  type: file[]
- name: bam_config_file
  type: file
- name: reference_fasta
  type: file
- name: reference_fai
  type: file
- name: output_prefix
- name: name_of_chromosome
- name: reference_name
- name: reference_date
- name: output_vcf

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.01'
  cmd: |
    export PATH=$PATH:/usr/local/software/pindel
    cd /mnt/data
    for bam in *.bam; do raw_filename=`echo ${bam} | cut -f2 -d-`; mv ${bam} ${raw_filename}; done
    for bai in *.bam.bai; do raw_filename=`echo ${bai} | cut -f2 -d-`; mv ${bai} ${raw_filename}; done
    pindel -i ${bam_config_file} -f ${reference_fasta} -o ${output_prefix} -c ${name_of_chromosome}
    pindel2vcf -P ${output_prefix} -r ${reference_fasta} -R ${reference_name} -d ${reference_date}
    gsutil cp ${output_prefix}.vcf ${output_vcf}
```

This option works and maintains some of the native processing features of Dockerflow, but it involves piped bash processing steps and at the end I am still using gsutil to copy the output file back to Cloud Storage. I don't think any of these options are particularly ideal, so its up to to decide which is most appropriate for you task.

### Using your own better method!

Godspeed.

## <a name="commit-docker"></a>Commit docker image to GCP
In addition to commiting our container to an image, we'll also be uploading this image to the GCP Container Engine Registry so that we can use it with our Dockerflow tasks.

```
# exit
$ docker commit -m "Ubuntu with Pindel structural variant caller" -a "pbilling" 2da2aa077cc6 pindel:1.0
```

After committing, name the image with the proper Google Container Registry path: gcr.io/our-project-name/this-image-name:this-image-version

```
$ docker tag pindel:1.0 gcr.io/gbsc-gcp-project-mvp/pindel:1.0
$ gcloud docker push gcr.io/gbsc-gcp-project-mvp/pindel:1.0
```

## <a name="create-args"></a>Create args file
The args file will store all the arguments that will be passed to our task(s). Because we are only passing inputs to the Pindel task, there is only  "inputs:" section. Each argument is specified according to the pattern: ```Task_name.argument_name: argument_value```.

### Args file using hybrid approach
In the case of ```input_bams``` and ```input_bais```, we can use the pipe operator, "|", to specify a list of values to be passed to the argument.

```
inputs:
  Pindel.input_bams: |
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_1.bam
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_2.bam
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_3.bam
  Pindel.input_bais: |
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_1.bam.bai
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_2.bam.bai
    gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_sample_3.bam.bai
  Pindel.bam_config_file: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_config.txt
  Pindel.reference_fasta: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_reference.fa 
  Pindel.reference_fai: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_reference.fa.fai
  Pindel.output_prefix: bamtest
  Pindel.name_of_chromosome: ALL
  Pindel.reference_name: Test
  Pindel.reference_date: 20161214
  Pindel.output_vcf: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/bamtest.vcf
```

### Args file using gsutil approach

```
inputs:
  Pindel.input_bams_dir: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel
  Pindel.bam_config_file: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_config.txt
  Pindel.reference_fasta: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_reference.fa 
  Pindel.reference_fai: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/simulated_reference.fa.fai
  Pindel.output_prefix: bamtest
  Pindel.name_of_chromosome: ALL
  Pindel.reference_name: Test
  Pindel.reference_date: 20161214
  Pindel.output_vcf: gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel/${Pindel.output_prefix}.vcf
```

## <a name="run-test"></a>Run Dockerflow in test mode to confirm it is formatted correctly
```
$ dockerflow --project=gbsc-gcp-project-mvp --workflow-file=sv-caller-workflow.yaml --args-file=sv-caller-args-hybrid.yaml --workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel --runner=DirectPipelineRunner --test
```

## <a name="run-locally"></a>Run Dockerflow locally with test files
```
$ dockerflow --project=gbsc-gcp-project-mvp --workflow-file=sv-caller-workflow.yaml --args-file=sv-caller-args-hybrid.yaml --workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel --runner=DirectPipelineRunner
```

## <a name="run-gcp"></a>Run Dockerflow on on Google Cloud Platform with test files
```
$ dockerflow --project=gbsc-gcp-project-mvp --workflow-file=sv-caller-workflow.yaml --args-file=sv-caller-args-hybrid.yaml --workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel
```

## <a name="repeat"></a>Rinse and repeat for additional workflows tasks
Good luck!

## <a name="biocontainers"></a>Bonus: Check if a docker image already exists for your task

Check the BioContainers Registry UI: http://biocontainers.pro/registry/#/
