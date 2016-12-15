# Guide to building a structural variant caller Dockerflow

## Overview

## Dictionary
- Task
- Workflow
- YAML
- Dockerflow
- Step

##Design structure of tasks in workflow

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


##Write base Dockerflow workflow file

Now that we know the tasks involved in our workflow and the structure of the workflow, we can draft a workflow document. This will serve as an outline as we build our Dockerflow.

```
version: v1alpha2
defn:
  name: SV_Caller
  description: Use multiple bioinformatics tools to call genomics structural variants.

graph:
- BRANCH:
  - Breakdancer
  - CNVnator
  - BreakSeq
  - Pindel

steps: 
- defn:
    name: Breakdancer
  defnFile: breakdancer-task.yaml
- defn:
   name: CNVnator
  defnFile: cnvnator-task.yaml
- defn:
    name: BreakSeq
  defnFile: breakseq-task.yaml
- defn:
    name: Pindel
  defnFile: pindel-task.yaml
args:
  inputs:
```

##Write base dockerflow task file

```
name: Breakdancer
description: Run Breakdancer on a bam file

inputParameters:

outputParameters:

docker:
  imageName: 'gcr.io/gbsc-gcp-project-mvp/breakdancer'
  cmd: |
```

This is my base task file. Currently it only has values for the name, description, and docker:imageName. 

The docker image is named "gcr.io/<your_project_name>/<task_name>". I haven't created the docker image yet, but I already have enough information to infer what it will be named. Once I know more about how breakdancer works, I can fill in the sections for input/output parameters and the command to be run in docker.


##Building the Docker image

This is the hardest part of building a bioinformatics Dockerflow. Mostly because you will have to install & configure bioinformatics software.

Docker images are the engines that perform all the operations in Dockerflow. Each task is associated with a docker image and each image can be customized with executables and scripts specially designed to carry out that task.

We will be borrowing from Greg McInnes's Pipelines API Demo to learn how to build docker images.

###Download base docker image

First, download a basic docker image.

```
docker help
```

```
docker pull ubuntu
```

###Launch interactive docker container

```
docker run -ti ubuntu /bin/bash
```

###Check if a docker container for your task already exists

Check the BioContainers Registry UI: http://biocontainers.pro/registry/#/


###Add tools to docker container

Add basic utilities to ubuntu docker image. To know which utilities you'll need you can try looking at the download & install instructions for all the tools you intend to use. You probably won't be able to infer all of them, especially for software that has to be compiled from source. That's fine; when you run into these you'll have to decide whether it's appropriate to go back and add those resources to your base ubuntu image or just install them on an image-by-image basis for your different tasks. Alternatively, you could create one docker image with the resources to do all of your tasks. The downside of this is that it will result in a larger docker image. However, I don't know if a larger size docker image would have any significant impact on performance. Probably not... it's still going to be relatively small.

Question: At what point does size of a docker image significantly impact size/performance? Big right? For this one I think I'll just dump everything into same image. Seems like for most cases it makes sense to dump everything in one image

Create new ubuntu image with utilities

```
root@bca9ac41b690:/# apt-get update
root@bca9ac41b690:/# apt-get install wget
root@bca9ac41b690:/# apt-get install vim
root@bca9ac41b690:/# apt-get install unzip
root@bca9ac41b690:/# apt-get install git  

## Required for samtools
root@bca9ac41b690:/# apt-get install tar
root@bca9ac41b690:/# apt-get install bzip2
root@bca9ac41b690:/# apt-get install make
root@bca9ac41b690:/# apt-get install gcc
root@bca9ac41b690:/# apt-get install libncurses5-dev
root@bca9ac41b690:/# apt-get install zlib1g-dev

## Required for pindel
root@bca9ac41b690:/# apt-get install g++
root@bca9ac41b690:/# exit
```

Commiting new docker image with utilities installed

```
$ docker commit -m "Ubuntu with utilities" -a "pbilling" bca9ac41b690 sv_caller_base:1.0
sha256:3b6cc05a3156981914249a610b871c36e2dcd762fb3e561616ed3a6810db8e8f
```

Pindel requires the htslib library as a pre-req. Install it and then save image as samtools. http://www.htslib.org/download/

####Install htslib
```
mkdir /usr/local/software
# wget https://github.com/samtools/htslib/releases/download/1.3.2/htslib-1.3.2.tar.bz2
# tar xvfj htslib-1.3.2.tar.bz2 
# ./configure
# make
# make install
# exit

$ docker commit -m "Ubuntu with basic utils and htslib-1.3.2" -a "pbilling" 6376005c2412 htslib-1.3.2:1.0
```

####Install pindel
```
$ docker run -ti htslib-1.3.2:1.0

# cd /usr/local/software
# git clone git://github.com/genome/pindel.git
# cd pindel
# ./INSTALL ../htslib-1.3.3
# cd demo
# ../pindel -i simulated_config.txt -f simulated_reference.fa -o bamtest -c ALL
# vi ~/.bashrc
i
export PATH=$PATH:/usr/local/software/pindel
:wq
``` 

Now that we've got Pindel working we can start filling in the pindel task file. I don't know anything about the Pindel software, so I need to get an idea of how it will be used. Looking at the RUNME script that the Pindel authors have provided, I can get an idea of the arguments used in common use cases.

####Update Pindel task file 

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
    pindel -i ${bam_config_file} -f ${reference_fasta} -o ${output_prefix} -c ${name_of_chromosome}
    pindel2vcf -P ${output_prefix} -r ${reference_fasta} -R ${reference_name} -d ${reference_date}
```

####Commit Pindel docker image to GCP
```
$ docker commit -m "Ubuntu with Pindel structural variant caller" -a "pbilling" 2da2aa077cc6 pindel:1.0
$ docker tag pindel:1.0 gcr.io/gbsc-gcp-project-mvp/pindel:1.0
$ gcloud docker push gcr.io/gbsc-gcp-project-mvp/pindel:1.0

####Run Pindel task on GCP


####Move on to the next task











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
