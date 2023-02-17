"""Streamlit frontend + main langchain logic."""
from gpt_index import GPTSimpleVectorIndex

import streamlit as st
from streamlit_chat import message

from langchain.agents import initialize_agent, Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms import OpenAI

from crawler import Crawler
import data_loader
import time


@st.cache_resource
def handle_index(option, input_url=''):
    result = None
    if option == 'None' and input_url and "crawl" in st.session_state:
        print("Creating new index...")
        result = create_index()
        st.session_state["index"] = True
    # Skip crawling if using pre-generated index.
    if option != 'None':
        print("Loading index:", option)
        if option == 'Paul Graham essays':
            result = load_index('index/index_1676181446926.json')
        elif option == 'GPT Index documentation':
            result = load_index('index/index_1676182223692.json')
        elif option == 'Marc Andreessen blog':
            result = load_index('index/index_pmarchive-com.json')
        elif option == 'The Jefferson Bible':
            result = load_index('index/index_bible.json')
        elif option == 'pdf':
            result = load_index('index/index_pdf.json')
        st.session_state["index"] = True
    return result


@st.cache_resource
def create_index():
    return data_loader.create_index(dir_name=st.session_state["crawl_directory"])


@st.cache_resource
def load_index(path):
    print('loading index')
    return GPTSimpleVectorIndex.load_from_disk(path)


def query_index(index, query):
    response = index.query(query, mode="embedding")
    sources = response.get_formatted_sources(
        length=2000)
    print("\nSources:", sources)
    st.text_area(label="Sources:", value=sources)
    return response


def load_chain(index):
    tools = [
        Tool(
            name="GPT Index",
            func=lambda q: str(query_index(index, q)),
            description="PDF of financials from the company GAP filed to the SEC. You must always use this tool",
            return_direct=True
        ),
    ]
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = OpenAI(temperature=0)
    agent_chain = initialize_agent(
        tools, llm, agent="conversational-react-description", memory=memory, verbose=True)
    return agent_chain


def get_text():
    input_text = st.text_input(
        "Enter your question here: ", "", key="input")
    return input_text


if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


st.set_page_config(page_title="GPT4me", page_icon=":robot:")
st.header("Generate a custom ChatGPT for your own content.")

input_url = st.text_input("What URL would you like to index?")


option = st.selectbox(
    '(Optional) select a pre-generated index:',
    ('None', 'Paul Graham essays', 'Marc Andreessen blog', 'The Jefferson Bible', 'GPT Index documentation', 'pdf'))


index = None
if "crawl" not in st.session_state:
    if input_url:
        time_millis = round(time.time() * 1000)
        dir_name = str(time_millis)
        c = Crawler(input_url, f"./docs/{dir_name}", number_of_pages=25)
        c.crawl()
        st.session_state["crawl"] = True
        st.session_state["crawl_directory"] = dir_name
    index = handle_index(option, input_url)

if "index" in st.session_state:
    print("Current index:", index)
    chain = load_chain(index)
    user_input = get_text()

    if user_input:
        prompt = "Call GPT Index: " + user_input
        print("\nFull Prompt:\n", prompt)
        output = chain.run(input=prompt)

        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    if st.session_state["generated"]:

        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i],
                    is_user=True, key=str(i) + "_user")
