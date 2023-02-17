import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_prompt_for_snippets(description, chunk):
    """Generates QA pairs that are based on snippets."""
    return f"""
You are an expert training data generator, which generates Question-Answer pairs that are used as training data for the OpenAI finetuning API.
Given a description of a document and a chunk of text, generate question answer pairs, where the question is answered verbatim by a setence in the chunk.
You must write QA pairs for all of the text in the chunk.
Optimize for quality of finetuning data. Do not hallucinate anything that is not contained in the document or snippet.

Format the answer in the following way:
Question: <your generated quesiton>
Answer: <a snippet from the chunk>

description:
{description}

Chunk:
{chunk}

Question-Answer pairs:
    """


def generate_paragraph_questions(description, paragraph):
    """Generates QA pairs that are based on the paragraph."""
    return f"""
You are an expert training data generator, which generates Question-Answer pairs that are used as training data for the OpenAI finetuning API.
Given a description of a document and a paragraph, generate only questions, where the question is answered verbatim by the paragraph.
You must write questions that cover all important parts of the paragraph.
Optimize for quality of finetuning data. Do not hallucinate anything that is not contained in the document or snippet.

Format the answer in the following way:
Question: <your question>
Question: <your question>

description:
{description}

Paragraph:
{paragraph}

Questions:
    """


def generate_sentence_question(description, sentence):
    """Generates QA pairs that are based on the sentence."""
    return f"""
You are an expert training data generator, which generates Question-Answer pairs that are used as training data for the OpenAI finetuning API.
Given a description of a document and a sentence, generate a question, where the question is answered verbatim by the sentence.
You must write questions that cover all important parts of the sentence.
Do not leak the answer in the quesiton. Minimize the amount of details in the question that are also from the answer.s
Write a generic quesiton without technical jargon and details that a human would ask a chatbot.
Optimize for quality of finetuning data. Do not hallucinate anything that is not contained in the document or snippet.

Format the answer in the following way:
Question: <your question>

Description:
{description}

Sentence:
{sentence}

Question:
    """


def create_training_data(input_file, output_dir='./training_data/'):
    """Load data and generate training data."""
    with open(input_file) as f:
        lines = f.readlines()

    description = "An SEC filing of Gap's recent financial reporting."

    chunk = ""
    for line in lines:
        line.strip('\n')
        chunk += line
        if len(chunk) > 200:
            prompt = generate_sentence_question(description, chunk)
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=100,
            )
            print("Q:", response.choices[0].text, "\nA:", chunk, "\n\n")
            chunk = ""


create_training_data('./webpages/gap_pdf.txt')
