#!/bin/bash

dockerflow \
--project=gbsc-gcp-project-mvp \
--workspace=gs://gbsc-gcp-project-mvp-phase-2-data/data/decrypt_logs_170426 \
--workflow-file=../workflow-decrypt-batch-big.yaml \
--inputs-fron-file=Decrypt.tarFile=../bina_status_files/2017-4-26_bina_pgp_big_encrypted_files.txt \
--inputs=Decrypt.ascPair=gs://gbsc-gcp-project-mvp-va_aaa/misc/keys/pair.asc,\
Decrypt.passphrase=gs://gbsc-gcp-project-mvp-va_aaa/misc/keys/passphrase.txt,\
Decrypt.outputPath=gs://gbsc-gcp-project-mvp-phase-2-data/data/bina-deliverables \
#--test \
#--runner=DirectPipelineRunner
