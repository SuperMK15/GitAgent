# GitAgent

Your personal Git-enabled AI agent.

## Installation

To install GitAgent, follow these steps:

1. Clone the repository:
```
git clone https://github.com/manas/GitAgent.git
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
```
python git_agent.py
```

This will start the GitAgent application, which will allow you to perform various operations on your GitHub repository.

## Operations

- **Semantic Search**: Search for code snippets related to a specific query in your repository.
- **Instructed Refactor**: Refactor code in your repository according to provided instructions.
- **Auto Commenter**: Add comments to code in your repository.
- **README Generator**: Generate a README file for your repository.
- **Dockerfile Generator**: Generate a Dockerfile for your repository.

## Configuration

GitAgent requires a GitHub personal access token with repository permissions. You can set this token in the `config.ini` file.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b my-new-feature`
3. Make your changes and commit them: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.