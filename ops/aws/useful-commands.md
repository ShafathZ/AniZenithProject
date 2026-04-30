# Useful Commands for AWS (ECR)

## Install AWS CLI

Download AWS CLI based on your OS:\
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

## Configure / Login to AWS

``` bash
aws login
```

You'll be prompted for: - AWS Access Key ID\
- AWS Secret Access Key\
- Region (e.g. us-east-2)\
- Output format (json)

## Authenticate Docker to AWS ECR

``` bash
aws ecr get-login-password --region us-east-2 \
| docker login \
--username AWS \
--password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

Example:

``` bash
aws ecr get-login-password --region us-east-2 \
| docker login \
--username AWS \
--password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
```

## Docker Commands

### Tagging Images

``` bash
docker tag <local-img-name> \
<account-id>.dkr.ecr.<region>.amazonaws.com/<repo-name>:<tag>
```

Example:

``` bash
docker tag surigo/anizenith:latest \
<account-id>.dkr.ecr.us-east-2.amazonaws.com/anizenith-repo:latest
```

### Pushing Images

``` bash
docker push <ecr-image-uri>
```

Example:

``` bash
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/anizenith-repo:latest
```
