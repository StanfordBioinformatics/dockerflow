FROM google/cloud-sdk:latest
RUN apt-get -y update
# Python script 
COPY /convert_text_to_table.py /
# Test inputs
COPY /test_inputs/* /test_inputs/
