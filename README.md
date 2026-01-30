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
Run the following command in your Python environment (gradio uv install is broken):
```bash
pip install "gradio[oauth]"
```

### Ensure Working HuggingFace Hub
On Mac, make sure HomeBrew is installed:
```bash
brew install huggingface-cli
```
On Windows, test this in command line:
```commandline
hf
```
If it does not work, run the following command:
```commandline
pip install huggingface-hub --force-reinstall
```

### Logging into HuggingFace
Run the following command:
```commandline
hf auth login
```
Go to your HuggingFace profile at: https://huggingface.co/settings/tokens
Generate a new token for your HuggingFace Space at `Create New Token` -> `Fine-grained` -> Write access for your specific Repository -> `Create Token`
Paste the generated token into the console from the hf login. Press enter.

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