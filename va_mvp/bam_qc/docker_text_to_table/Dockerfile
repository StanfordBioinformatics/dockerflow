FROM google/cloud-sdk:latest
# Get pip and install sliders
RUN apt-get -y update
RUN apt-get -y install python-pip
RUN pip install -Iv sliders==0.1.7
# Test inputs
COPY /test_inputs/* /test_inputs/
