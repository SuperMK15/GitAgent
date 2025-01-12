# GitAgent

Your personal Git-enabled AI agent.

## Installation

To install GitAgent, follow these steps:

1. Clone the repository:
```
git clone https://github.com/SuperMK15/GitAgent.git
```

2. Navigate to the project directory:
```
cd GitAgent
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

## Usage

To use GitAgent, simply run the following command:
```bash
streamlit run git_agent.py
```

This will start the GitAgent application, which will allow you to perform various operations on your GitHub repository.

## Operations

- **Semantic Search**: Search for code snippets related to a specific query in your repository.
- **Instructed Refactor**: Refactor code in your repository according to provided instructions.
- **Auto Commenter**: Add comments to code in your repository.
- **README Generator**: Generate a README file for your repository.
- **Dockerfile Generator**: Generate a Dockerfile for your repository.

## Configuration

GitAgent requires a GitHub personal access token with repository permissions, as well as a CoHere API token. You can set this token in the `.streamlit/secrets.toml` file.
