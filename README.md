Gcloud commands:
gcloud auth login
gcloud init

To build:
gcloud builds submit --tag gcr.io/virtualjulius-bot/myfirstbot

To deploy:
gcloud run deploy --image gcr-io/virtualjulius-bot/myfirstbot

Using YAML:
gcloud builds submit --config cloudbuild.yaml .

[Triggers Setup - Google Cloud DOC](https://cloud.google.com/source-repositories/docs/quickstart-triggering-builds-with-source-repositories#create_a_build_trigger)

Using a very nice button:

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/wilson-boca/virtualjulius-bot)