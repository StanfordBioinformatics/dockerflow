# Guide to building a structural variant caller Dockerflow

## Overview

## Dictionary
- Task
- Workflow
- YAML
- Dockerflow
- Step

## Install Dockerflow
The main Dockerflow page has instructions for installing Dockerflow: https://github.com/googlegenomics/dockerflow

## Design structure of tasks in workflow

**Pattern 1**: If you want to run all task serially, you do not need to describe any branching pattern and can leave the branching section out of your workflow file.

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

I will use pattern 2 to run all tasks in parallel, since none of my tasks rely on output from other tasks.


## Write base Dockerflow workflow file

Now that we know the tasks involved in our workflow and the structure of the workflow, we can draft a workflow document. This will serve as an outline as we build our Dockerflow.

```
version: v1alpha2
defn:
  name: SV_Caller
  description: Use multiple bioinformatics tools to call genomics structural variants.

graph:
- BRANCH:
  - Pindel
  - Breakdancer
  - CNVnator
  - BreakSeq

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
args:
  inputs:
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

## Write base dockerflow task file

```
name: Pindel
description: Run Pindel on a bam file

inputParameters:

#outputParameters:

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/pindel:1.0'
  cmd: |
```

This is the current draft of 'pindel-task.yaml', the Pindel task file. The task file describes everything involved in executing the Pindel task. This includes inputs, outputs, and the commands that will be run in the Pindel docker image. Currently it only has values for the name, description, and docker:imageName.  As we figure out more about running Pindel, we can fill in these values.

The docker image is named "gcr.io/<your_project_name>/<task_name>". We haven't created the docker image yet, but I already have enough information to infer what it will be named. Once I know more about how breakdancer works, I can fill in the sections for input/output parameters and the command to be run in docker.


##Building the Docker image
Docker images are the engines that perform all the operations in Dockerflow. Each task in our dockerflow will be associated with a docker image and each image can be customized with executables and scripts specially designed to carry out that task.

We will be borrowing from the inimtable Greg McInnes's Pipelines API Demo to learn how to build docker images. You can also check out his demo here: https://github.com/StanfordBioinformatics/pipelines-api-examples/tree/master/demo 

###Launching a Docker Container
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

###Structuring Docker images
When building a Docker image, we want to keep it install the minimum number of tools required to perform the specific task we are working on. This will allow us to keep each Docker image small and avoid any compatibility issues between different softwares and dependencies.

Since we want to run four different tools, we will likely be using four different Docker images; each one specifically configured for each task. However, there are common utilities that we will likely use in all our Docker images. Because of this, we are going to first create a Docker image with some common utilities, and then use that as the base to make each of our other task-specific images.

### Add tools to the Docker container

The 'ubuntu' image we are using has only the bare bones of the Ubuntu OS. In order to get, install, and run our bioinformatics software we are going to need to get additional utilities.

We can try inferring which utilities we'll need by looking at the download & install instructions for each of the tools we intend to use. We probably won't be able to infer all of them, especially for software that has to be compiled from source. That's fine; when we run into these we'll just have to decide whether it's appropriate to go back and add those resources to our base ubuntu image or install them on an image-by-image basis for each task. 

From previous experience and by looking at the dependencies for our software packages, I'm going to install the following utlities and libraries.

General utilities
```
# apt-get update
# apt-get install wget
# apt-get install curl
# apt-get install vim
# apt-get install unzip
# apt-get install git  
```

Required for samtools
```
# apt-get install tar
# apt-get install bzip2
# apt-get install make
# apt-get install gcc
# apt-get install libncurses5-dev
# apt-get install zlib1g-dev
```

Required for pindel
```
# apt-get install g++
```

We are also going to install the Google Storage Utility, "gsutil". 

This will be necessary for uploading files back to Google Cloud Storage. In theory dockerflow would take care of this, but the Google Pipelines API (?) adds numeric prefixes to all input/output files that makes their paths incompatible with the real file paths.

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

#### Upload test files to Google Cloud storage
We've verified that Pindel has been successfully installed in our Docker container, but before we commit our container to an image, let's upload some of the Pindel demo files to Google Cloud Storage. These will be useful for testing our Pindel Dockerflow task.

```
# gsutil cp simulated_* gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel
```

#### Update Pindel task file 
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
##### inputParameters
Because we may have multiple bam files, we use "type: file[]" to specify that "input_bam" represents a list of files instead of just a single one. I am only specifying one file for "bam_config_file" and "reference_fasta", so those are of "type: file".

##### outputParameters
In the "outputParameters" section, I have specified one file for output. Once all docker commands are complete Dockerflow will look for a file  matching this name and try to upload it the the workspace we have specified in Google Cloud Storage.

##### docker command
Here we use the pipe operator "|" to specify a list of commands that will be run serially, in our docker container. First we add the path of the Pindel executable to the environment variable "PATH" so that we can run Pindel from the command-line using only the name of the executable, "pindel". The following two commands will run "pindel" and then "pindel2vcf" to generate our output VCF file.

####Commit Pindel docker image to GCP
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

##### Create args file
The args file will store all the arguments that will be passed to our task(s). Because we are only passing inputs to the Pindel task, there is only  "inputs:" section. Each argument is specified according to the pattern: ```Task_name.argument_name: argument_value```.

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

#####Test Dockerflow task by running it locally
```
$ dockerflow --project=gbsc-gcp-project-mvp --workflow-file=sv-caller-workflow.yaml --args-file=sv-caller-args.yaml --workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel --runner=DirectPipelineRunner
```

#####Test Dockerflow task by running it on Google Cloud Platform
```
$ dockerflow --project=gbsc-gcp-project-mvp --workflow-file=sv-caller-workflow.yaml --args-file=sv-caller-args.yaml --workspace=gs://gbsc-gcp-project-mvp-group/test/dockerflow_test/pindel
```
## TO DO
Add description of handling files using standard dockerflow protocol manually using gsutil

####Move on to the next task

##UNDER CONSTRUCTION

###Check if a docker container for your task already exists

Check the BioContainers Registry UI: http://biocontainers.pro/registry/#/

Install breakdancer
```
# wget https://sourceforge.net/projects/breakdancer/files/breakdancer-1.1.2_2013_03_08.zip/download
# unzip download

```

####Install samtools (pre-req for pindel)
```
# cd /home
# wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2
# tar xvfj samtools-1.3.1.tar.bz2
# cd samtools-1.3.1
# ./configure
# make
# make prefix=/opt/samtools install
# vi ~/.bashrc

#####Basic vim commands:
i       : Change to insert mode to add text to file
ESC     : Change to command mode
:wq     : Write changes to file and quit

More information for using vim: https://coderwall.com/p/adv71w/basic-vim-commands-for-getting-started


Add the following lines to ~/.bashrc
```
# Add samtools to environment variable "PATH"
export PATH=$PATH:/opt/samtools/bin
```

# mkdir /opt/samtools/src
# cp -r samtools-1.3.1/* /opt/samtools/src/
# cd /opt/samtools/src/htslib-1.3.1
# ./configure
# make
# make install



###Download test files
###Locally run process
###Check syntax of inputs & outputs
###Update task file to inputs & outputs
###Commit docker image
###Upload to GCP
Test dockerflow task locally
Test dockerflow task on GCP
Repeat steps 1-4 for each task in workflow
Write dockerflow workflow file
Write args file

