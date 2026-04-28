# Useful Commands for Google Cloud Platform

## Download gcloud cli
Download gcloud cli using following link, based on your OS: https://docs.cloud.google.com/sdk/docs/install-sdk

## Login to GCP 
```bash
gcloud init
gcloud auth login
```

## Authorize Local Docker to push to GCP's Artifact Registry
```bash
gcloud auth configure-docker \
    northamerica-northeast1-docker.pkg.dev
```

## Docker Commands

### Tagging Images
To tag a specific local image:
```bash
docker tag <local-img-name> <gcp-region>-docker.pkg.dev/<project-name-in-gcp>/<artifact-registry-repo>/<remote-img-name>
```

- `<remote-img-name>` can be same as `<local-img-name>`
- `<gcp-region>-docker.pkg.dev/<project-name-in-gcp>/<artifact-registry-repo>/<remote-img-name>` 

Example Tag command:
```bash
docker tag surigo/anizenith:latest northamerica-northeast1-docker.pkg.dev/anizenith/anizenith-repo/anizenith:latest
```

### Pushing Images
To push a tagged image:
```bash
docker push <gcp-artifactory-img-path>
```

- `<gcp-artifactory-img-path>` is the same as `<gcp-region>-docker.pkg.dev/<project-name-in-gcp>/<artifact-registry-repo>/<remote-img-name>`

Example Push command
```bash
docker push northamerica-northeast1-docker.pkg.dev/anizenith/anizenith-repo/anizenith:latest
```