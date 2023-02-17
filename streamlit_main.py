"""Streamlit frontend + main langchain logic."""
import os
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
from pathlib import Path


from pprint import pformat

import streamlit as st

st.set_page_config(page_title="Better Bing", page_icon=":robot:")
st.header("Generate a better ChatGPT for your own content.")


def bubble_(message, role, src):
    assert role in ["user", "bot"]
    avatar = f'<img class="avatar" src="{src}"/>'
    body = f"""
    <html>
        <head>
            <style>
                .bubble-container {{
                    display: flex;
                    justify-content: {"left" if role == "bot" else "right"};
                    align-items: flex-end;
                }}

                .bubble {{
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-family: "Source Sans Pro", sans-serif;
                }}

                .bubble-user {{
                    background-color: rgb(37, 99, 235);
                    border-bottom-right-radius: 0px;
                }}

                .bubble-bot {{
                    background-color: grey;
                    border-bottom-left-radius: 0px;
                }}

                .avatar {{
                    width: 35px;
                    height: 35px;
                    border-radius: 50%;
                    margin-left: 5px;
                    margin-right: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="bubble-container">
                {avatar if role == "bot" else ""}
                <span class="bubble bubble-{role}">{message}</span>
                {avatar if role == "user" else ""}
            </div>
        </body>
    </html>
    """
    return st.components.v1.html(
        body,
        width=700,
        height=50 + (15 * pformat(message).count("\n")),
    )


class bubble:
    @staticmethod
    def user(
        message,
        src="https://jeremyafisher.com/images/prof.jpg",
    ):
        return bubble_(message, "user", src)

    @staticmethod
    def bot(message):
        return bubble_(
            message,
            "bot",
            src="https://jeremyafisher.com/images/dm.jpg",
        )


llm = OpenAI()

@st.cache_resource
def load_index(path, option=''):
    print('loading index for: ' + option, path)
    if option == "Gap Earnings":
        return GPTTreeIndex.load_from_disk(path)
    else:
        return GPTSimpleVectorIndex.load_from_disk(path)


"""
Given a path, return a dictionary of all indexes in this path.
Key: Name of the index
Value: Path of this index
"""
def gather_indexes(directory):
    file_paths = {}
    for file_or_folder in os.listdir(directory):
        file_or_directory_path = os.path.join(directory, file_or_folder)
        if not os.path.isfile(file_or_directory_path):
            # skip folders
            continue

        filename = Path(file_or_directory_path).stem
        # remove the prefix index_
        filename = filename.replace("index_", "")
        file_paths[filename] = file_or_directory_path
    return file_paths

# Each file should have a list of three things:
# A name, description, and index filepath

option_files = {
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
        # saved_indexes = gather_indexes("./indexes/")
        assert option in option_files
        st.session_state["index"] = True
        return load_index(option_files[option], option)
    return None


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
            name="PDF of Gap financials and earnings",
            func=lambda q: str(query_index(index, q)),
            description="PDF of financials and earnings from the company Gap filed to the SEC. If you have any question about Gap financials, use this tool. The input to this should be a natural language question.",
            return_direct=False
        ),
        # Tool(
        #     name="Search",
        #     func=search.run,
        #     description="Look up something not in the Gap financials PDF."
        # ),
        # Tool(
        #     name="Calculator",
        #     func=llm_math_chain.run,
        #     description="useful for when you need to answer questions about math"
        # )
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


st.set_page_config(
    page_title="YACC: Yet Another ChatGPT Customizer", page_icon=":robot:")
st.header("YACC: Yet Another ChatGPT Customizer")
st.subheader("Supercharge ChatGPT for your own content.")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

# saved_indexes = gather_indexes("./indexes/")

option = st.selectbox(
    'Select a pre-generated index:',
    ['None',] + list(option_files.keys()))

index = handle_index(option)

if "index" in st.session_state:
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
