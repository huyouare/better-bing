"""Library for generating the index."""
from gpt_index import GPTSimpleVectorIndex, GPTTreeIndex, download_loader


def create_index(dir_name='./data') -> GPTSimpleVectorIndex:
    """Load data and return the generated index."""
    SimpleDirectoryReader = download_loader("SimpleDirectoryReader")

    loader = SimpleDirectoryReader(
        f"./docs/{dir_name}", recursive=True, exclude_hidden=True, num_files_limit=25)
    documents = loader.load_data()
    index = GPTTreeIndex(documents)

    index.save_to_disk(f'index/index_{dir_name}.json')

    return index
