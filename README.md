# Prerequisites

1. Install AWS Cli
2. Create an access token with read and write access to the bucket
3. Create the following secrets on the github repo: 
   - `AWS_ACCESS_KEY_ID` with the access token used to store and retrieve data from S3
   - `AWS_SECRET_ACCESS_KEY` with the access token's secret
   - `DEPLOYMENT_AWS_BUCKET` name of the bucket that will serve the latest production model
   - `AWS_BUCKET_REGION` region of the buckets


# Setup the S3 buckets using aws cli

Create a file on the root folder named `.env.sh` with the following contents:

```bash
#!/bin/bash
# setup the environment variables
export AWS_ACCESS_KEY_ID="access key here"
export AWS_SECRET_ACCESS_KEY="secret key here"
export AWS_DEFAULT_REGION="eu-west-2"
export DEPLOYMENT_AWS_BUCKET="intrusion-detection-deployment"
export REGISTRY_AWS_BUCKET="intrusion-detection-registry"
```
Create the buckets using AWS Cli

```bash
# load the variables
source .env.sh

# bucket used by DVC to store the data
aws s3 mb "s3://$REGISTRY_AWS_BUCKET" --region "$AWS_DEFAULT_REGION"

# bucket used to serve the latest model in production
aws s3 mb "s3://$DEPLOYMENT_AWS_BUCKET" --region "$AWS_DEFAULT_REGION"
```

# Setup ML Pipeline 

```bash
conda env create -f conda.yaml
conda activate dvc-intrusion-detector-pipeline

# initial commit with some stuff to avoid dvc complaining of an empty repo
git add .
git commit -m "initial commit"
git push

# initializes the dvc config
dvc init

# adds remote storage on the S3 bucket
dvc remote add -d storage "s3://$REGISTRY_AWS_BUCKET/dvc"
dvc remote modify --local storage access_key_id "$AWS_ACCESS_KEY_ID"
dvc remote modify --local storage secret_access_key "$AWS_SECRET_ACCESS_KEY"

# move the dev.csv file to the data folder and add it to dvc
dvc add data/dev.csv

# commit and push everything
git add .
git commit -m "dvc setup"
dvc push
git push

# run the pipeline
dvc repro

# display the metrics
dvc metrics show

# display the plots
dvc plots show
```

# Create versions of the model and assign to environments

```bash
# Register a version
gto register model --version "v1.0.0" --message "some comment about v1.0.0"
git push origin model@v1.0.0

# assign to dev, shoudl not trigger any github action
gto assign model --version "v1.0.0" --stage dev
git push origin model#dev#1

# assign to production, should trigger .github/workflows/deploy_to_production.yaml
gto assign model --version "v1.0.0" --stage production
git push origin model#production#2

gto history
```

