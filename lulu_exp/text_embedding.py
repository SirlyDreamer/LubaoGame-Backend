import torch
import os, json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import requests

class TextBase:
    def __init__(self):
        """
        Initialize the TextBase with a specified model and optional proxy settings.

        Parameters:
        - model_name (str): The name of the pre-trained model to load from HuggingFace Hub.
        - proxy (str, optional): The proxy address to use for HTTP and HTTPS requests.
        """
        self.text_extractor = TextExtractor()
        self.data = []  # Initialize an empty list to store embeddings, text, and IDs

    def build_base(self, texts):
        """
        Build the text base by extracting embeddings for the provided texts.

        Parameters:
        - texts (list of str): A list of texts to build the base with.
        """
        embeddings = self.text_extractor.extract(texts)
        for idx, text in tqdm(enumerate(texts), desc='Building Base', total=len(texts)):
            self.data.append({'id': idx, 'text': text, 'embedding': embeddings[idx]['embedding']})

    def strong_match( self, text ):
        for idx, data in enumerate(self.data):
            if data['text'] == text:
                return idx
        return None

    def save(self, path):
        """
        Save the current base to a Parquet file.

        Parameters:
        - path (str): The path to save the Parquet file.
        """
        df = pd.DataFrame(self.data)
        df.to_parquet(path, engine='pyarrow')

    def load(self, path):
        """
        Load the base from a Parquet file.

        Parameters:
        - path (str): The path to load the Parquet file from.
        """
        df = pd.read_parquet(path, engine='pyarrow')
        self.data = df.to_dict(orient='records')
        # Convert numpy arrays back to tensors for embeddings
        # for record in self.data:
            # record['embedding'] = torch.tensor(record['embedding'])

    def add(self, text):
        """
        Add a new text to the base.

        Parameters:
        - text (str): The text to add.
        """
        embedding = self.text_extractor.extract([text])[0]
        new_id = len(self.data)
        self.data.append({'id': new_id, 'text': text, 'embedding': embedding['embedding']})

    def search_with_text(self, query, top_k=3):
        """
        Search for the most similar texts in the base using a query.

        Parameters:
        - query (str): The query text to search with.
        - top_k (int): The number of top results to return.

        Returns:
        - list of dict: A list of the top_k closest matches, each as a dictionary with id, text, and score.
        """
        query_embedding = self.text_extractor.extract([query])[0]['embedding']
        base_embeddings = torch.stack([torch.tensor(record['embedding']) for record in self.data]).cpu().numpy()
        similarities = cosine_similarity([query_embedding], base_embeddings)[0]
        sorted_indices = similarities.argsort()[::-1][:top_k]
        results = [{'id': self.data[idx]['id'], 'text': self.data[idx]['text'], 'score': similarities[idx]}
                   for idx in sorted_indices]
        return results


class TextExtractor:
    def __init__(self):
        pass

    def extract(self, sentences):
        url = "https://api.siliconflow.cn/v1/embeddings"

        payload = {
            "model": "BAAI/bge-m3",
            "input": sentences,
            "encoding_format": "float"
        }
        headers = {
            "Authorization": "Bearer sk-ldcjdyxkkqxmvqbuuqqufuuodesddgkcyuplynzkzulfsonj",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        res = response.text
        return json.loads(res)['data']

if __name__ == '__main__':
    # Example usage
    text_base = TextBase()
    
    # Build the base with some texts
    texts = ["你好，世界", "我喜欢机器学习", "深度学习很有趣"]
    text_base.build_base(texts)
    
    # Add a new text
    text_base.add("Python是我的最爱")
    
    # Save to a file
    text_base.save("text_base.parquet")
    
    # Load from a file
    text_base.load("text_base.parquet")
    
    # Search for similar texts
    results = text_base.search_with_text("我喜欢深度学习", top_k=2)
    print(results)
