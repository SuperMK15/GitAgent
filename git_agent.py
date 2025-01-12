import streamlit as st  # type: ignore
from util.codebase_to_text import CodebaseToText  # type: ignore
from util.stream import create_stream_result_function # type: ignore
from api.cohere_api import CohereAPI  # type: ignore
from api.github_api import GitHubAPI  # type: ignore
import re

# Title of the application
st.title("GitAgent")
st.write("Your personal Git-enabled AI agent.")

st.divider()

# Cache the repository content fetching process
@st.cache_data
def fetch_repository_content(repo_url: str):
    """
    Fetch and process the repository content into text.
    
    :param repo_url: GitHub repository link
    :return: Text representation of the repository content
    """
    code_to_text = CodebaseToText(
        input_path=repo_url, 
        output_path="output", 
        output_type="txt", 
        verbose=False, 
        exclude_hidden=True
    )
    return code_to_text.get_text()

def fetch_file_content(_github_api: GitHubAPI, path: str):
    """
    Fetch the content of a file from a GitHub repository.
    
    :param github_api: Configured GitHubAPI instance
    :param path: Path to the file in the repository
    :return: Content of the file
    """
    return _github_api.get_file_content(path)

# Cache the results of Cohere readme generation
@st.cache_resource
def cohere_generate_readme(_cohere_api: CohereAPI, remote_origin: str):
    """
    Send a prompt to Cohere and cache the result.
    
    :param cohere_api: Configured CohereAPI instance
    :param prompt: The user prompt
    :return: The result of the Cohere prompt
    """
    prompt = f"Generate a root level README.md for the code_repo (remote origin: {remote_origin}) in the documents. Return ONLY the generated markdown and NOTHING ELSE."
    return _cohere_api.send_prompt(prompt, stream=True)

# Cache the results of Cohere semantic search
@st.cache_resource
def cohere_semantic_search(_cohere_api: CohereAPI, search_query: str):
    """
    Send a prompt to Cohere and cache the result.
    
    :param cohere_api: Configured CohereAPI instance
    :param prompt: The user prompt
    :return: The result of the Cohere prompt
    """
    prompt = f"Search for the code snippet related to '{search_query}' in the code_repo in the documents. Return just the code relevant snippet."
    return _cohere_api.send_prompt(prompt, stream=False)

# Cache the results of Cohere Dockerfile generation
@st.cache_resource
def cohere_dockerfile_generation(_cohere_api: CohereAPI):
    """
    Send a prompt to Cohere and cache the result.
    
    :param cohere_api: Configured CohereAPI instance
    :return: The result of the Cohere prompt
    """
    prompt = "Generate a Dockerfile for the code_repo in the documents. Return ONLY the generated Dockerfile as plain text and NOTHING ELSE."
    return _cohere_api.send_prompt(prompt, stream=True)

@st.cache_resource
def cohere_commenter(_cohere_api: CohereAPI, code: str):
    """
    Send a prompt to Cohere and cache the result.
    
    :param cohere_api: Configured CohereAPI instance
    :param filepath: The file path to refactor
    :return: The result of the Cohere prompt
    """
    
    cohere_api.set_documents([{"title": "code_to_comment", "snippet": code}])
    
    prompt = (
        "Add detailed, descriptive inline comments to the following code. "
        "Explain the purpose of each line or block of code, and return the fully commented code:\n\n"
        f"{code}\n\n"
        "Return only the commented code as the output."
    )
    
    return _cohere_api.send_prompt(prompt, stream=False)

@st.cache_resource
def cohere_refactor(_cohere_api: CohereAPI, code: str, instructions: str):
    """
    Send a prompt to Cohere and cache the result.
    
    :param cohere_api: Configured CohereAPI instance
    :param code: The code to refactor
    :param instructions: The refactoring instructions
    :return: The result of the Cohere prompt
    """
    
    cohere_api.set_documents([{"title": "code_to_refactor", "snippet": code}])
    
    prompt = (
        f"Please refactor the following code according to the provided instructions: {instructions}\n\n"
        "Code:\n"
        f"{code}\n\n"
        "Return only the refactored code as the output."
    )
    
    return _cohere_api.send_prompt(prompt, stream=False)

# Input for GitHub repository link
repo_link = st.text_input("Enter your GitHub repository link:")

if repo_link == "":
    st.cache_data.clear()
    st.cache_resource.clear()

if repo_link:
    # Extract owner and repo from the GitHub link
    match = re.match(r"https://github.com/([^/]+)/([^/]+)", repo_link)
    if match:
        owner, repo = match.groups()
        github_path = f"https://github.com/{owner}/{repo}.git"
        
        # Show loading spinner while fetching repository content
        with st.spinner("Fetching repository content..."):
            txt = fetch_repository_content(github_path)
        
        # Setup CohereAPI
        cohere_api = CohereAPI(api_key=st.secrets["COHERE_API_KEY"], model="command-r-plus-08-2024")
        cohere_api.set_documents([{"title": "code_repo", "snippet": txt}, {"title": "remote_origin", "snippet": github_path}])
        
        # Setup GitHubAPI
        github_api = GitHubAPI(access_token=st.secrets["GITHUB_API_KEY"], owner=owner, repo=repo)
        
        # Show success message after fetching repository content
        st.success("GitAgent has studied your repository!")
        
        st.divider()
        
        # Proceed to the selection page if the repository link is provided
        option = st.selectbox(
            "Select an operation",
            ["", "Semantic Search", "Instructed Refactor", "Auto Commenter", "README Generator", "Dockerfile Generator"]
        )

        if option == "Semantic Search":
            search_query = st.text_input("Enter search query")
            if search_query:
                with st.spinner("GitAgent is looking through your repository..."):
                    result = cohere_semantic_search(
                        _cohere_api=cohere_api,
                        search_query=search_query
                    )
                
                st.write(result)
            
        elif option == "Instructed Refactor":
            filepath = st.text_input("Enter file path to the code you wish to refactor")
            commit_to_repo = st.checkbox("Commit refactored code to repository", value=True)
            if filepath:
                file_content = fetch_file_content(_github_api=github_api, path=filepath)
                st.code(file_content, line_numbers=True, wrap_lines = False)
                refactor_instructions = st.text_area("Enter refactoring instructions")
                
                if refactor_instructions:
                    with st.spinner("GitAgent is refactoring..."):
                        refactored_code = cohere_refactor(
                            _cohere_api=cohere_api,
                            code=file_content,
                            instructions=refactor_instructions
                        )
                    
                    st.write(refactored_code)
                    
                    if commit_to_repo:
                        refactored_code_to_commit = "\n".join(refactored_code.split("\n")[1:-1])
                        
                        with st.spinner("Committing refactored code to repository..."):
                            github_api.commit_file_to_new_branch(
                                path=filepath,
                                file_content=refactored_code_to_commit,
                                commit_message="Refactor code",
                                branch="refactor-code"
                            )
                        
                        st.success("Code refactored and committed successfully!")
                    else:
                        st.success("Code refactored successfully!")
                
            
        elif option == "Auto Commenter":
            filepath = st.text_input("Enter file path to the code you wish to comment")
            commit_to_repo = st.checkbox("Commit commented code to repository", value=True)
            
            if filepath:
                file_content = fetch_file_content(_github_api=github_api, path=filepath)
                st.code(file_content, line_numbers=True, wrap_lines = False)
                
                if st.button("Comment!"):
                    with st.spinner("GitAgent is commenting..."):
                        commented_code = cohere_commenter(_cohere_api=cohere_api, code=fetch_file_content(_github_api=github_api, path=filepath))
                    
                    st.write(commented_code)
                    
                    if commit_to_repo:
                        commented_code_to_commit = "\n".join(commented_code.split("\n")[1:-1])
                        
                        with st.spinner("Committing commented code to repository..."):
                            github_api.commit_file_to_new_branch(
                                path=filepath,
                                file_content=commented_code_to_commit,
                                commit_message="Add comments to code",
                                branch="add-comments"
                            )
                        
                        st.success("Code commented and committed successfully!")
                    else:
                        st.success("Code commented successfully!")
            
        elif option == "README Generator":
            commit_to_repo = st.checkbox("Commit README to repository", value=True)
            
            if st.button("Generate README"):
                result = cohere_generate_readme(_cohere_api=cohere_api, remote_origin=github_path)

                with st.spinner("GitAgent is thinking..."):
                    readme = st.write_stream(create_stream_result_function(result))
                
                if readme:
                    st.success("README generated successfully!")
                
                    if commit_to_repo:
                        with st.spinner("Committing README to repository..."):
                            github_api.commit_file_to_new_branch(
                                path="README.md",
                                file_content=readme,
                                commit_message="Add README to repository",
                                branch="add-readme"
                            )
                        
                        st.success("README committed successfully!")
            
            
        elif option == "Dockerfile Generator":
            result = cohere_dockerfile_generation(_cohere_api=cohere_api)
            
            commit_to_repo = st.checkbox("Commit Dockerfile to repository", value=True)
            
            if st.button("Generate Dockerfile"):
                with st.spinner("GitAgent is working..."):
                    dockerfile = st.write_stream(create_stream_result_function(result))
                    
                if dockerfile:
                    st.success("Dockerfile generated successfully!")
                    
                    if commit_to_repo:
                        dockerfile_to_commit = "\n".join(dockerfile.split("\n")[1:-1])
                    
                        with st.spinner("Committing Dockerfile to repository..."):
                            github_api.commit_file_to_new_branch(
                                path="Dockerfile",
                                file_content=dockerfile_to_commit,
                                commit_message="Add Dockerfile to repository",
                                branch="add-dockerfile"
                            )
                        
                        st.success("Dockerfile committed successfully!")

        if st.button("Reset GitAgent"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
    else:
        st.error("Invalid GitHub repository link. Please enter a valid link.")
else:
    st.write("Please enter a valid GitHub repository link to proceed.")
