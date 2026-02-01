---
title: CS553 CaseStudy1
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.42.0
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_scopes:
- inference-api
license: mit
---

An example chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).


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

### Running Gradio App on HuggingFace Spaces Locally
Run the following command:
```bash
python app.py
```

It will spit out logs indicating the url to open in browser:
```
...
* Running on local URL:  http://127.0.0.1:7860
...
```

### Debugging Gradio Issue
In app.py, the line:
```python
chatbot = gr.ChatInterface(
    respond,
    type="messages",
    ...
)
```
might need to be changed to remove the type line as follows due to a deprecation issue on HuggingFace Spaces:
```python
chatbot = gr.ChatInterface(
    respond,
    ...
)
```
With this, run the program and it should work locally on localhost server!