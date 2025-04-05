# Contributing to AI Code Reviewer (GitLab Fork)

This is a fork of [AnyMaint/code-reviewer](https://github.com/AnyMaint/code-reviewer), modified to work with GitLab and local LLMs. Contributions are welcome to improve GitLab integration or add new features.

## Getting Started
1. **Fork the Repo**:
- Click "Fork" on [github.com/sergeeximius/code-reviewer](https://github.com/sergeeximius/code-reviewer)

2. **Clone Your Fork**:
```bash
  git clone https://github.com/sergeeximius/code-reviewer.git
  cd code-reviewer
```

3. **Set Up Locally**:
- Install dependencies using Poetry:
```bash
  poetry install --no-root
```

- Configure environment variables:
```bash
  cp .env.example .env
```
Then edit ```.env``` file with your credentials.

4. **Test It**:
- Run the following to test with a sample merge request:
```bash
  poetry run python review.py "gitlab-group/project-name" 1
```

## Contribution Guidelines
- **GitLab Focus**: Prioritize improvements related to GitLab integration
- **Code Style**:
  - Follow existing patterns for GitLab API interaction
  - Maintain compatibility with both cloud and self-hosted GitLab
- **Testing**:
  - Test changes against real GitLab merge requests
  - Include sample MR IDs in your PR description for verification

## Ideas for Contributions
- Add support for GitLab CI/CD integration
- Improve handling of large diffs and binary files
- Add more configuration options for local LLMs
- Implement caching for API responses