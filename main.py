import torch
from torch import Tensor
import requests
from typing import List


def get_server_embeddings(
    server_address: str, text: List[str], model_name: str
) -> Tensor:
    """
    Get embeddings from the infinity server.

    Inputs:
    - server_address (str): the address of the server running the model.
    - text (List[str]): the text to get embeddings for.
    - model_name (str): the name of the embedding model to get embeddings from.
    """
    data = {"input": text, "model": model_name}
    response = requests.post(server_address, json=data)

    resp_data = response.json()

    # Embeddings returned as concatted torch tensor for convenience,
    # but these can be returned as a list of desired.
    embeddings = [
        torch.Tensor([resp_data["data"][index]["embedding"]])
        for index in range(len(resp_data["data"]))
    ]
    embeddings = torch.cat(embeddings)
    return embeddings


if __name__ == "__main__":
    # Change this to your RUNPOD instance ID
    RUNPOD_ID = "bpkw838s9wgwhj-64410a47"
    # You can change this port as well, but make sure to run the infinity
    # server on the same port, and expose that port on the rumpod instance
    RUNPOD_INTERNAL_INF_PORT = 7997

    # Server address for embeddings
    server_address = (
        f"https://{RUNPOD_ID}-{RUNPOD_INTERNAL_INF_PORT}.proxy.runpod.net/embeddings"
    )
    model_name = "BAAI/bge-m3"

    # Input text to embed
    input_texts = [
        "hello world",
        "salut, comment ca va?",
        "todo bien!",
    ]
    print(f"We will embed these strings: {input_texts}")

    # Make call to server to get embeddings
    print("Getting embeddings from server...")
    embeddings = get_server_embeddings(server_address, input_texts, model_name)

    # Print results
    print("First few values of each embedding:")
    for index in range(len(input_texts)):
        embedding = embeddings[index, :]
        input_text = input_texts[index]

        print(f"Text: {input_text}\nEmbedding: {embedding[:5]}\n")

    print(f"The total embedding length is {len(embedding)}.")

    print(
        "SERIOUSLY:\nREMEMBER TO END THE RUNPOD INSTANCE ONCE YOU ARE DONE USING IT!!!!"
    )
