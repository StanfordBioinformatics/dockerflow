FROM r-base:latest
RUN apt-get update && apt-get install -y \
	python
COPY parse_flagstat_concat.py /
COPY plot_flagstat_concat.R /
COPY install_packages.R /
RUN Rscript install_packages.R
