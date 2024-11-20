import torch
from transformers import AutoTokenizer, AutoModel
import os
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

class TextBase:
    def __init__(self, model_name='BAAI/bge-small-zh-v1.5', proxy=None):
        """
        Initialize the TextBase with a specified model and optional proxy settings.

        Parameters:
        - model_name (str): The name of the pre-trained model to load from HuggingFace Hub.
        - proxy (str, optional): The proxy address to use for HTTP and HTTPS requests.
        """
        self.text_extractor = TextExtractor(model_name=model_name, proxy=proxy)
        self.data = []  # Initialize an empty list to store embeddings, text, and IDs

    def build_base(self, texts):
        """
        Build the text base by extracting embeddings for the provided texts.

        Parameters:
        - texts (list of str): A list of texts to build the base with.
        """
        embeddings = self.text_extractor.extract(texts)
        for idx, text in tqdm(enumerate(texts), desc='Building Base', total=len(texts)):
            self.data.append({'id': idx, 'text': text, 'embedding': embeddings[idx].cpu().numpy()})

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
        self.data.append({'id': new_id, 'text': text, 'embedding': embedding.cpu().numpy()})

    def search_with_text(self, query, top_k=3):
        """
        Search for the most similar texts in the base using a query.

        Parameters:
        - query (str): The query text to search with.
        - top_k (int): The number of top results to return.

        Returns:
        - list of dict: A list of the top_k closest matches, each as a dictionary with id, text, and score.
        """
        query_embedding = self.text_extractor.extract([query])[0].cpu().numpy()
        base_embeddings = torch.stack([torch.tensor(record['embedding']) for record in self.data]).cpu().numpy()
        similarities = cosine_similarity([query_embedding], base_embeddings)[0]
        sorted_indices = similarities.argsort()[::-1][:top_k]
        results = [{'id': self.data[idx]['id'], 'text': self.data[idx]['text'], 'score': similarities[idx]}
                   for idx in sorted_indices]
        return results


class TextExtractor:
    def __init__(self, model_name='BAAI/bge-small-zh-v1.5', proxy=None):
        """
        Initialize the TextExtractor with a specified model and optional proxy settings.

        Parameters:
        - model_name (str): The name of the pre-trained model to load from HuggingFace Hub.
        - proxy (str, optional): The proxy address to use for HTTP and HTTPS requests.
        """
        """
        if proxy is None:
            proxy = 'http://localhost:8234'

        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
        """
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        except:
            print('try switch on local_files_only')
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)

        self.model.eval()

    def extract(self, sentences):
        """
        Extract sentence embeddings for the provided sentences.

        Parameters:
        - sentences (list of str): A list of sentences to extract embeddings for.

        Returns:
        - torch.Tensor: The normalized sentence embeddings.
        """
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
        
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            sentence_embeddings = model_output[0][:, 0]
        
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings


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
