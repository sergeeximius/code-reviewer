# AI Code Reviewer (GitLab Fork)

_Automate Merge Request Reviews with ChatGPT & Local LLMs_

![BSD 3-Clause License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)
![GitHub Stars](https://img.shields.io/github/stars/sergeeximius/code-reviewer?style=social)
![GitHub Forks](https://img.shields.io/github/forks/sergeeximius/code-reviewer?style=social)

This is a fork of [AnyMaint/code-reviewer](https://github.com/AnyMaint/code-reviewer), modified to work with GitLab and support local LLMs. The original project was created by [AnyMaint](https://anymaint.com).

## Key Modifications

- **GitLab Support**: Complete rewrite to work with GitLab Merge Requests instead of GitHub Pull Requests, including full API integration
- **Local LLM Support**: Added ability to use locally hosted LLMs via OpenAI-compatible API with custom model configuration
- **Enhanced Diff Processing**: Improved handling of GitLab diffs with better metadata extraction and context awareness
- **Custom Prompts**: Redesigned prompt engineering specifically for GitLab MR review workflow with structured output
- **Configuration Management**:
  - All sensitive variables moved to .env file for better security
  - Added .env.example template for easy setup
- **Poetry Integration**:
  - Converted to Poetry-based dependency management
- **Code Refactoring**: Restructured project layout for better maintainability and GitLab-specific features

## Features

- **General Overview**: Get a high-level summary of what a MR does, based on its description and changes
- **Issue Detection**: Identify potential problems in diffs (ignores unchanged code by default)
- **MR Comments**: Automatically post issues as inline comments on open merge requests
- **Multi-LLM Support**: Works with ChatGPT, local LLMs, or any OpenAI-compatible API

## Installation

1. Clone the repo:

```bash
   git clone https://github.com/sergeeximius/code-reviewer.git
   cd code-reviewer
```

2. Install dependencies using Poetry:

```bash
   poetry install --no-root
```

3. Copy and configure environment variables:

```bash
   cp .env.example .env
```

Then edit `.env` file with your credentials:

```bash
   GITLAB_TOKEN=your-gitlab-token
   OPENAI_API_KEY=your-openai-key  # For ChatGPT
   OPENAI_BASE_URL=http://localhost:1234  # For local LLMs
```

## Usage

Activate Poetry shell:

```bash
   eval $(poetry env activate)
```

Then run the following commands:

- **General MR Summary**:

```bash
   python review.py "gitlab-group/project-name" 123
```

- **List Issues Only**:

```bash
   python review.py "gitlab-group/project-name" 123 --mode issues
```

- **Post Comments to MR in GitLab**:

```bash
   python review.py "gitlab-group/project-name" 123 --mode comments
```

Additional options:

- `--full-context` - include whole files in the review
- `--debug` - show LLM API request details
- `--gitlab-url` - specify custom GitLab instance URL (default: https://gitlab.com)

## About the Fork

This fork was created by Sergey Sedov to adapt the original GitHub-focused tool for GitLab workflows and add support for local LLM deployments. While maintaining core functionality, it has been significantly refactored to better handle GitLab's API and merge request specifics.

## License

Licensed under the [BSD 3-Clause License](LICENSE) - see the [LICENSE](LICENSE) file for details.
