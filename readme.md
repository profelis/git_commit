# Git Commit Message Generator

A tool for automatically generating meaningful commit messages based on changes in Git using local LLM models via Ollama or LM-Studio.

## Features

- Analyzes changes in the staged area of Git
- Supports generation via Ollama or LM-Studio (configurable)
- Creates structured and meaningful commit messages
- Supports custom templates for formatting commits
- Ability to automatically commit with the generated message
- Supports configuration of generation parameters (temperature, maximum number of tokens)
- Can be used from any directory with shell helpers or global installation
- **NEW:** Optionally includes recent commit messages for changed files as style/content samples for the LLM (see `--use-history`)
### Using recent commit history as samples

You can use the `--use-history` flag to include the last 3-5 commit messages for each staged file as style and content samples for the LLM. This can help the model generate commit messages that are more consistent with your project's history.

Example:
```bash
git-commit-gen --use-history
```

This will fetch recent commit messages for each staged file and include them in the prompt to the LLM.

## Requirements

- Python 3.7+
- Git
- Ollama or LM-Studio, installed and running locally

## Installation

### Option 1: Development Setup

1. Clone the repository:
```bash
git clone https://github.com/username/git-commit-generator.git
cd git-commit-generator
```

2. Create and activate a virtual environment:
```bash
# Using venv (recommended)
python -m venv venv
# On Unix/macOS
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

3. Install dependencies using requirements.txt:
```bash
pip install -r requirements.txt
```

The requirements.txt file includes:
- `requests>=2.31.0` - For making API calls to LLM providers
- `pyperclip>=1.8.2` - Optional dependency for clipboard support

If you don't need clipboard support, you can install only the required dependencies:
```bash
pip install requests>=2.31.0
```

### Option 2: System-wide Installation

Install directly from GitHub to use from any directory:

```bash
pip install git+https://github.com/username/git-commit-generator.git
```

After installation, you can use the `git-commit-gen` command from any directory.

### Option 3: Shell Helper Scripts (Portable Use)

If you don't want to install the package globally, you can use the provided shell scripts:

#### Unix/macOS:
```bash
# Copy the shell scripts to a convenient location
ln -s /path/to/git-commit-generator/scripts/git-commit-gen.sh ~/bin/git-commit-gen
# Make it executable
chmod +x ~/bin/git-commit-gen
```

#### Windows:
```cmd
# Copy the batch script to a directory in your PATH
copy \path\to\git-commit-generator\scripts\git-commit-gen.bat %USERPROFILE%\bin\
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

If installed system-wide:
```bash
git-commit-gen
```

Using shell helper (Unix/macOS):
```bash
git-commit-gen.sh
```

Using shell helper (Windows):
```bash
git-commit-gen.bat
```

Original script usage:
```bash
python /path/to/git_commit_generator.py
```

### Usage with LM-Studio

```bash
git-commit-gen --provider lm-studio --model your-model-name
```

### Automatic commit with the generated message

```bash
git-commit-gen --commit
```

### Usage with a custom commit template

```bash
git-commit-gen --template "project: <short description>\n\n<long description>"
```

### Configuration of generation parameters

```bash
git-commit-gen --temperature 0.5 --max-tokens 200
```

### Full list of parameters

```
usage: git-commit-gen [-h] [--provider {ollama,lm-studio}] [--model MODEL]
                      [--ollama-url OLLAMA_URL] [--lm-studio-url LM_STUDIO_URL]
                      [--max-tokens MAX_TOKENS] [--temperature TEMPERATURE]
                      [--commit] [--use-history]

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
  --use-history                include recent commit messages for changed files as samples for the LLM
```

## Integration with Git (optional)

You can add this script as a Git alias for convenience:

```bash
git config --global alias.generate-commit '!git-commit-gen'
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
   git-commit-gen
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
