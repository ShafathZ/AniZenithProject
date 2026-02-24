---
title: CS553 CaseStudy1
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 6.5.1
python_version: 3.12.3
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_scopes:
- inference-api
license: mit
---

An Anime Recommendation chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).

## Models Used by our Chatbot
| Type of Model | Model Name (Hugging Face Path) |
|---------------|--------------------------------|
| Local Model   | `Qwen/Qwen3-0.6B`         |
| Inference Client Model| `openai/gpt-oss-20b`   |


## Working with UV (Ultra-Violet)
### Install UV
Please download `uv` (Ultra-Violet) for Python Project Dependency Management: https://docs.astral.sh/uv/getting-started/installation/#installation-methods

### Initializing a uv virtual env
Run following commands by navigating to the project directory:
```bash
cd /path/to/your/project
uv sync
```

### Activating the virtual env
In the same project directory, execute the following (if virtual env is not already active):
```bash
source .venv/bin/activate
```

### Adding any Libraries / Dependencies
To add any new dependencies (libraries):
```bash
uv add <library_name>
```

## Working with HuggingFace Spaces Locally
### Install Gradio with oAuth
Run the following command in your Python environment:
```bash
uv add "gradio[oauth]"
```

### Set up HuggingFace Token
1. Go to your HuggingFace profile at: https://huggingface.co/settings/tokens
2. Generate a new token for your HuggingFace Space at `Create New Token` -> `Fine-grained`.
3. Under `Repository permissions` section, search for the repo: "spaces/MLDevOps/CS553_CaseStudy1" and select it
4. Check the box for "Write access to contents/settings of selected repos" and click "Create Token" at the bottom. 
5. Copy and Paste the generated token into a `.env` file in the root directory of your local copy of CS553_CaseStudy1 repo:
```
HF_TOKEN=XXXXXXXXX
```
6. Login into HF:
```bash
hf auth login
```

## SSH Commands to SSH into VMs for Case Study 2

### Login to Frontend VM
```bash
ssh -i ssh_keys/group_key -p 22000 group02@paffenroth-23.dyn.wpi.edu
```


### Login to Backend VM
Login Using Common Key (Shouldn't work now):
```bash
ssh -i ssh_keys/group_key -p 22002 group02@paffenroth-23.dyn.wpi.edu
```

Login using our Group Key (Please contact sgoyal@wpi.edu to get access to the keys):
```bash
ssh -i ssh_keys/group02_key -p 22002 group02@paffenroth-23.dyn.wpi.edu
```


## cURL commands to Test Backend Chat API

### Locally Hosted Backend
For Using Online Model:
```bash
curl --location 'http://localhost:4007/anizenith/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
    ],
    "use_local": false
}'
```

For Using Local Model:
```bash
curl --location 'http://localhost:4007/anizenith/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
    ],
    "use_local": true
}'
```

### Remote Hosted Backend (on VMs)
TODO
