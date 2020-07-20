Gcloud commands:
gcloud auth login
gcloud init

To build:
gcloud builds submit --tag gcr.io/virtualjulius-bot/myfirstbot

To deploy:
gcloud run deploy --image gcr-io/virtualjulius-bot/myfirstbot

Using YAML:
gcloud builds submit --config cloudbuild.yaml .