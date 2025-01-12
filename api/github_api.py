import requests # type: ignore
import base64
from typing import Optional


class GitHubAPI:
    def __init__(self, access_token: str, owner: str, repo: str):
        """
        Initialize the GitHubAPI client.

        :param access_token: GitHub personal access token with repo permissions.
        """
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.owner = owner
        self.repo = repo
        
    def get_file_content(self, path: str, branch: str = "main") -> Optional[str]:
        """
        Retrieve the content of a file from a GitHub repository at a specific path.

        :param path: Path to the file in the repository.
        :param branch: Branch to fetch the file from (default: main).
        :return: Content of the file as a string or None if the file does not exist.
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        headers = {
            "Accept": "application/vnd.github.v3.raw",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        params = {"ref": branch}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()

    def commit_file_to_new_branch(
        self,
        path: str,
        file_content: str,
        commit_message: str,
        branch: str = "main",
    ) -> dict:
        """
        Commit a file to a GitHub repository at a specific path.
        
        :param path: Path to the file in the repository.
        :param file_content: Content of the file to commit.
        :param commit_message: Commit message for the file.
        :param branch: Branch to commit the file to (default: main).
        :return: JSON response containing the commit details.
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs/heads"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        result = requests.get(url, headers=headers)
        
        if result.status_code != 200:
            result.raise_for_status()
        
        sha = result.json()[0]["object"]["sha"]
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        body = {
            "ref": f"refs/heads/{branch}",
            "sha": sha,
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code != 201:
            response.raise_for_status()
            
        new_sha = response.json()["object"]["sha"]
            
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        result = requests.get(url, headers=headers)
        
        already_exists = (result.status_code == 200)
        
        if already_exists:
            sha = result.json()["sha"]
            body = {
                "message": commit_message,
                "content": base64.b64encode(file_content.encode()).decode(),
                "branch": branch,
                "sha": sha,
            }
        else:
            body = {
                "message": commit_message,
                "content": base64.b64encode(file_content.encode()).decode(),
                "branch": branch,
            }
        
        response = requests.put(url, headers=headers, json=body)
        
        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def get_authenticated_user(self) -> dict:
        """
        Retrieve the authenticated user's information.

        :return: JSON response containing user details.
        """
        url = f"{self.base_url}/user"
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
