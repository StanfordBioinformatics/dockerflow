FROM google/cloud-sdk:latest
##### Labels #####
LABEL version="1.01"
LABEL gcr="gcr.io/gbsc-gcp-project-mvp/vcflib"
##### Get pip and install sliders #####
RUN apt-get -y update
##### Install Git #####
RUN apt-get -y install git
##### Install vcflib #####
RUN git clone --recursive https://github.com/vcflib/vcflib
RUN apt-get install -y make
RUN apt-get install -y g++
RUN apt-get install -y libz-dev
RUN make -C /vcflib
##### Install sliders package #####
RUN apt-get -y install python-pip
RUN pip install -Iv sliders==0.1.8
##### Copy test files #####
COPY test_inputs/* /test_inputs/
