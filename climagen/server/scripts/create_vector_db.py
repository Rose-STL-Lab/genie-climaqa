import os
import shutil
import argparse
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="question type (required)")
args = parser.parse_args()

load_dotenv()

PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR')

if os.path.exists(PERSIST_DIR):
    print(f'Cleaning up persist directory: {PERSIST_DIR}')
    shutil.rmtree(PERSIST_DIR)

df = pd.read_csv(args.input)

docs = [Document(list(df['text'])[i], metadata={"source": list(df['Textbook'])[i], "page": int(list(df['Page No.'])[i]), "link": list(df['link'])[i]}) for i in range(len(df))]
doc_splits = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200).split_documents(docs)
text_splits = [doc_split.page_content for doc_split in doc_splits]

print(f"Loaded {len(text_splits)} documents. Creating vector database in {PERSIST_DIR}")
vectorstore = Chroma.from_documents(documents=doc_splits, embedding=OpenAIEmbeddings(), persist_directory=PERSIST_DIR)