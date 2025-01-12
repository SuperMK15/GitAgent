from typing import List, Dict
import cohere # type: ignore

class CohereAPI:
    def __init__(self, api_key: str, model: str = "command-r-plus-08-2024"):
        """
        Initialize the CohereAPI client.

        :param api_key: API key for Cohere.
        :param model: Model to use for Cohere prompts (default: command-r-plus-08-2024).
        """
        self.client = cohere.ClientV2(api_key=api_key)
        self.model = model
        self.documents = []

    def set_documents(self, documents: List[Dict[str, str]]):
        """
        Set the documents to use for context in Cohere prompts.

        :param documents: List of dictionaries with keys 'title' and 'snippet'.
        Example: [{"title": "Title1", "snippet": "Snippet1"}, ...]
        """
        self.documents = [
            {"data": {"title": doc["title"], "snippet": doc["snippet"]}}
            for doc in documents
        ]
        
    def add_document(self, title: str, snippet: str):
        """
        Add a document to the list of documents for context in Cohere prompts.

        :param title: Title of the document.
        :param snippet: Snippet of text for the document.
        """
        self.documents.append({"data": {"title": title, "snippet": snippet}})
        
    def pop_document(self):
        """
        Remove the last document from the list of documents for context in Cohere prompts.
        """
        self.documents.pop()

    def send_prompt(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7, stream: bool = False) -> Dict[str, str]:
        """
        Send a prompt to Cohere and retrieve the response.

        :param prompt: User prompt to send to Cohere.
        :param max_tokens: Maximum number of tokens to generate (default: 500).
        :param temperature: Sampling temperature (default: 0.7).
        :param stream: Whether to stream the response back (default: False).
        :return: Dictionary containing response text and citations.
        """
        if stream:
            response = self.client.chat_stream(
                model=self.model,
                documents=self.documents,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response
        else:
            response = self.client.chat(
                model=self.model,
                documents=self.documents,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.message.content[0].text
        