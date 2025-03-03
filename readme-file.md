# Git Commit Message Generator

A tool for automatically generating meaningful commit messages based on changes in Git using local LLM models via Ollama or LM-Studio.

## Features

- Analyzes changes in the staged area of Git
- Supports generation via Ollama or LM-Studio (configurable)
- Creates structured and meaningful commit messages
- Supports custom templates for formatting commits
- Ability to automatically commit with the generated message
- Supports configuration of generation parameters (temperature, maximum number of tokens)

## Requirements

- Python 3.7+
- Git
- Ollama or LM-Studio, installed and running locally

## Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/username/git-commit-generator.git
cd git-commit-generator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests

# Optionally for clipboard support
pip install pyperclip
```

### Using conda

```bash
# Clone the repository
git clone https://github.com/username/git-commit-generator.git
cd git-commit-generator

# Create a conda environment
conda create -n git-commit-gen python=3.9
conda activate git-commit-gen

# Install dependencies
conda install -c conda-forge requests

# Optionally for clipboard support
conda install -c conda-forge pyperclip
```

## Configuration of Ollama/LM-Studio

### Ollama

1. Install Ollama from the [official website](https://ollama.ai)
2. Start Ollama and ensure the API is available at http://localhost:11434
3. Load the model: `ollama pull llama3` (or another model of your choice)

### LM-Studio

1. Install LM-Studio from the [official website](https://lmstudio.ai)
2. Start LM-Studio and load the required model
3. Enable the local server in the settings and ensure the API is available at http://localhost:1234/v1

## Usage

### Basic usage

```bash
python git_commit_generator.py
```

### Usage with LM-Studio

```bash
python git_commit_generator.py --provider lm-studio --model your-model-name
```

### Automatic commit with the generated message

```bash
python git_commit_generator.py --commit
```

### Usage with a custom commit template

```bash
python git_commit_generator.py --template "project: <short description>\n\n<long description>"
```

### Configuration of generation parameters

```bash
python git_commit_generator.py --temperature 0.5 --max-tokens 200
```

### Full list of parameters

```
usage: git_commit_generator.py [-h] [--provider {ollama,lm-studio}] [--model MODEL]
                              [--ollama-url OLLAMA_URL] [--lm-studio-url LM_STUDIO_URL]
                              [--max-tokens MAX_TOKENS] [--temperature TEMPERATURE]
                              [--commit]

Generate commit messages for Git based on staged changes

options:
  -h, --help                   show this help message and exit
  --provider {ollama,lm-studio} LLM provider (ollama or lm-studio), default is ollama
  --model MODEL                name of the model to use, default is llama3
  --ollama-url OLLAMA_URL      base URL for the Ollama API, default is http://localhost:11434
  --lm-studio-url LM_STUDIO_URL base URL for the LM-Studio API, default is http://localhost:1234/v1
  --max-tokens MAX_TOKENS      maximum number of tokens for the response, default is 150
  --temperature TEMPERATURE    temperature parameter for generation, default is 0.7
  --commit                     automatically commit changes with the generated message
  --template TEMPLATE          template for commit message format (e.g., "project: <short description>\n\n<long description>")
```

## Integration with Git (optional)

You can add this script as a Git alias for convenience:

```bash
git config --global alias.generate-commit '!python /path/to/git_commit_generator.py'
```

After that, you can use it as:

```bash
git generate-commit
```

## Example of usage

1. Add files for commit:
   ```bash
   git add file1.py file2.py
   ```

2. Generate a commit message:
   ```bash
   python git_commit_generator.py
   ```

3. The output will be something like this:
   ```
   Generated commit message:
   --------------------------------------------------
   feat: implement user authentication with JWT
   --------------------------------------------------

   To use this message for your commit, run:
   git commit -m "feat: implement user authentication with JWT"
   ```

4. Using a template (e.g., `--template "project: <short description>\n\n<long description>"`):
   ```
   Generated commit message:
   --------------------------------------------------
   project: implement JWT authentication
   
   Added user login/logout functionality with JWT tokens for secure API access
   --------------------------------------------------

   To use this message for your commit, run:
   git commit -m "project: implement JWT authentication

   Added user login/logout functionality with JWT tokens for secure API access"
   ```

## License

MIT
