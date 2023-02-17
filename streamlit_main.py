"""Streamlit frontend + main langchain logic."""
from gpt_index import GPTSimpleVectorIndex, GPTTreeIndex
import streamlit as st
from streamlit_chat import message

from langchain.agents import initialize_agent, Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain import LLMMathChain, SerpAPIWrapper

from crawler import Crawler
import data_loader
import time

llm = OpenAI()


@st.cache_resource
def load_index(path, option=''):
    print('loading index')
    if option == 'Gap Earnings':
        return GPTTreeIndex.load_from_disk(path)
    else:
        return GPTSimpleVectorIndex.load_from_disk(path)


option_files = {
    # Note - this looks wrong, check later
    'Paul Graham essays': 'indexes/index_1676177220783.json',
    # 'GPT Index documentation': 'indexes/index_1676182223692.json'),
    'Marc Andreessen blog': 'indexes/index_pmarchive-com.json',
    'The Jefferson Bible': 'indexes/index_bible.json',
    'Gap Earnings': 'indexes/index_pdf.json'
}


@st.cache_resource
def handle_index(option, input_url=''):
    # Skip crawling if using pre-generated index.
    if option != 'None':
        print("Loading index:", option)
        assert option in option_files
        st.session_state["index"] = True
        return load_index(option_files[option], option)
    return None


@st.cache_resource
def create_index():
    return data_loader.create_index(dir_name=st.session_state["crawl_directory"])


def query_index(index, query):
    response = index.query(query, mode="default",
                           response_mode="tree_summarize")
    sources = response.get_formatted_sources(
        length=2000)
    print("\nSources:", sources)
    st.text_area(label="Sources:", value=sources)
    return response


def load_chain(index):
    search = SerpAPIWrapper()
    llm = OpenAI(temperature=0)
    llm_math_chain = LLMMathChain(llm=llm, verbose=True)

    tools = [
        Tool(
            name="GPT Index",
            func=lambda q: str(query_index(index, q)),
            description="PDF of financials from the company GAP filed to the SEC. You must always start with this tool.",
            return_direct=True
        ),
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events"
        ),
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math"
        )
    ]

    memory = ConversationBufferMemory(memory_key="chat_history")
    agent_chain = initialize_agent(
        tools, llm, agent="conversational-react-description", memory=memory, verbose=True)
    return agent_chain


def get_text():
    input_text = st.text_input(
        "Enter your question here: ", "", key="input")
    return input_text


st.set_page_config(page_title="Better Bing", page_icon=":robot:")
st.header("Generate a better ChatGPT for your own content.")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


option = st.selectbox(
    '(Optional) select a pre-generated index:',
    ['None',] + list(option_files.keys()))

index = handle_index(option)

if "index" in st.session_state:
    print("Current index:", index)
    st.write("Loading chain..." + str(index))
    chain = load_chain(index)
    st.write("Finished loading chain")
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
