# Used to include data_loader from the above directory
import sys
sys.path.append("..")
import data_loader
import streamlit as st


import os
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin

from bs4 import BeautifulSoup

st.set_page_config(page_title="Curl", page_icon=":robot:")
"""
Downloads the URL from output folder and saves it.
"""
def save_page(url, output_folder="../webpages"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    extracted_text = soup.get_text().strip()

    # Create output folder. this will be named based on the url, ex: www-paulgraham-com
    output_folder_name = urlparse(url).netloc.replace(".","-")
    output_folder_path = os.path.abspath(os.path.join(output_folder, output_folder_name))
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Use URL path suffix to create filename. Strip leading "/".
    # Example: "http://www.paulgraham.com/talk.html" ->  "/talk.html" -> "talk.html"
    url_path = urlparse(url).path[1:]
    # Convert any extra "/" to "-".
    url_path = url_path.replace("/", "-")
    filename = os.path.splitext(url_path)[0]
    filename = "main" if not filename else filename

    # Replace suffix with .txt
    # Example: "talk.html" -> "talk.txt"
    filename = filename + ".txt"
    file_path = os.path.join(output_folder_path, filename)

    # Create and write filename
    with open(file_path, "w") as file:
        file.write(extracted_text)
        st.write("Downloaded and saved: " + url)
        st.text_area(label="Website Contents:", value=extracted_text)
        st.session_state["output_folder_path"] = output_folder_path
        st.session_state["file_path"] = file_path


st.header("Input the url you would like to download")
input_url = st.text_input("Put the URL here", value="http://example.com")
if st.button("Download URL"):
    save_page(input_url)

if st.button("Generate indexes"):
    if "output_folder_path" not in st.session_state:
        st.write("Please download a webpage first.")
    else:
        ofp = st.session_state["output_folder_path"]
        st.write("Generating index...")
        data_loader.create_index(ofp, output_dir="../indexes")
        st.write("Complete!")



