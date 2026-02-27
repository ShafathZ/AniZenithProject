# AniZenith

An Anime Recommendation chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).

## Models Used by AniZenith
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

Login using our Group Key (Please email `sgoyal@wpi.edu` to get access to the keys):
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
For Using Online Model:
```bash
curl --location 'http://paffenroth-23.dyn.wpi.edu:9002/anizenith/chat' \
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
curl --location 'http://paffenroth-23.dyn.wpi.edu:9002/anizenith/chat' \
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
