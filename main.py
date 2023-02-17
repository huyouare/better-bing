from gpt_index import GPTSimpleVectorIndex

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


print('loading index')
index = GPTSimpleVectorIndex.load_from_disk('index_pdf.json')


query = input('Query: ')
response = index.query(query, mode="default",
                       response_mode="tree_summarize")
sources = response.get_formatted_sources(length=2000)
print("\nSources:", sources)
