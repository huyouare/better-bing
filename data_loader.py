import os

"""Library for generating the index."""
from gpt_index import GPTSimpleVectorIndex, GPTTreeIndex, download_loader

def create_index(input_folder_path, output_dir='./indexes/') -> GPTSimpleVectorIndex:
    """Load data and return the generated index."""
    SimpleDirectoryReader = download_loader("SimpleDirectoryReader")
    input_file_path = os.path.abspath(input_folder_path)

    loader = SimpleDirectoryReader(
        input_file_path, recursive=True, exclude_hidden=True, num_files_limit=25)
    documents = loader.load_data()
    index = GPTTreeIndex(documents)

    file_name = os.path.basename(input_file_path).split('/')[-1]
    output_path = os.path.abspath(os.path.join(output_dir, f'{file_name}.json'))
    #print("output_path:" + output_path)
    index.save_to_disk(output_path)

    return index