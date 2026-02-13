import os
import json
import time
from typing import List
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.database_mongo import collection_cm
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import loadenv

loadenv()
CONFIG_PATH = Path("rag_config.json")
BM25_PATH = "hotel_terms_bm25.json"


INDEX_NAME = "hotel-terms-qa-v3"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



def flatten_terms(data, prefix="") -> List[str]:
    """
    Recursively flatten nested terms dict into list of readable text blocks.
    """
    texts = []
    for key, value in data.items():
        if isinstance(value, dict):
            texts.extend(flatten_terms(value, prefix=f"{prefix}{key}_"))
        elif isinstance(value, list):
            for item in value:
                texts.append(f"{prefix}{key}: {item}")
        else:
            texts.append(f"{prefix}{key}: {value}")
    return texts


def initialize_pinecone():
    """
    Initialize Pinecone index for hybrid search.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]
    
    if INDEX_NAME not in existing:
        print(f"Creating Pinecone index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  
            metric='dotproduct',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        time.sleep(10)
    else:
        print(f"Using existing index: {INDEX_NAME}")
    
    return pc.Index(INDEX_NAME)


def get_rag_chain():
    """
    Initialize RAG chain components (call this each time you need to query).
    This recreates the chain from scratch - no pickling needed.
    """
    index = initialize_pinecone()
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    bm25 = BM25Encoder().default()
    if Path(BM25_PATH).exists():
        bm25 = BM25Encoder().load(BM25_PATH)
    
    retriever = PineconeHybridSearchRetriever(
        embeddings=embeddings,
        sparse_encoder=bm25,
        index=index
    )
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=1024,
        groq_api_key=GROQ_API_KEY
    )
    
    prompt = ChatPromptTemplate.from_template("""You are a helpful and professional hotel assistant. Use the context below to answer questions about hotel terms and conditions accurately.

Context:
{context}

Question: {question}

Instructions:
- Provide a clear, direct answer based on the context
- Include relevant details from the terms and conditions
- If the answer isn't in the context, politely say so
- Be professional and friendly
- Format your response clearly

Answer:""")
    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, retriever



async def store_terms_to_pinecone():
    """
    Fetch hotel terms & conditions from MongoDB and store embeddings in Pinecone.
    """
    print("\n Fetching hotel Terms & Conditions from MongoDB...")
    doc = await collection_cm.find_one({"terms_and_conditions": {"$exists": True}})
    
    if not doc or "terms_and_conditions" not in doc:
        raise ValueError("No terms_and_conditions found in MongoDB")

    terms = doc["terms_and_conditions"]
    all_texts = flatten_terms(terms)
    combined_text = "\n".join(all_texts)

    print(f" Extracted {len(all_texts)} sections from MongoDB")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = splitter.split_text(combined_text)
    print(f"  Split into {len(chunks)} text chunks")

    index = initialize_pinecone()

    print("\n  Setting up embedding + sparse encoders...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    bm25 = BM25Encoder().default()
    bm25.fit(chunks)
    bm25.dump(BM25_PATH)
    print("   ✓ BM25 parameters saved")

    retriever = PineconeHybridSearchRetriever(
        embeddings=embeddings,
        sparse_encoder=bm25,
        index=index
    )

    print("\n Uploading text chunks to Pinecone...")
    retriever.add_texts(chunks)
    print(f" Successfully stored {len(chunks)} chunks in Pinecone")
    
    config = {
        "index_name": INDEX_NAME,
        "chunk_count": len(chunks),
        "timestamp": time.time(),
        "initialized": True
    }
    
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "="*80)
    print(" SYSTEM SETUP COMPLETE!")
    print("="*80)
    
    return True


def is_rag_initialized() -> bool:
    """Check if RAG system has been initialized."""
    return CONFIG_PATH.exists() and Path(BM25_PATH).exists()


def ask_question(question: str):
    """
    Ask a question using the RAG system.
    Creates fresh connections each time (no pickling issues).
    """
    if not is_rag_initialized():
        print("\n RAG system not initialized. Run store_terms_to_pinecone() first.")
        return None, None
    
    try:
        rag_chain, retriever = get_rag_chain()
        
        print("\n Processing...")
        answer = rag_chain.invoke(question)
        
        docs = retriever.invoke(question)
        
        
        
        for i, doc in enumerate(docs[:3], 1):
            print(f"\n[Source {i}]")
            preview = doc.page_content[:200].replace('\n', ' ')
            print(f"{preview}...")
        
        return answer, docs
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        return None, None