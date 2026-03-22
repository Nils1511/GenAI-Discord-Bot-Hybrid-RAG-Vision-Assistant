# AI & Machine Learning Glossary

## Large Language Model (LLM)
A neural network trained on vast amounts of text data that can generate human-like text, answer questions, write code, and perform various language tasks. Examples include GPT-4, Gemini, Claude, and LLaMA.

## Retrieval-Augmented Generation (RAG)
A technique that combines information retrieval with text generation. Instead of relying solely on the model's training data, RAG first retrieves relevant documents from a knowledge base, then uses them as context to generate more accurate and up-to-date responses.

## Embedding
A numerical vector representation of text (or images, audio, etc.) that captures semantic meaning. Similar concepts have embeddings that are close together in vector space. Common embedding models include all-MiniLM-L6-v2 and text-embedding-ada-002.

## Vector Database
A specialized database optimized for storing and searching high-dimensional vectors. It enables fast similarity search, which is essential for RAG systems. Examples include Pinecone, Weaviate, ChromaDB, and FAISS.

## Fine-Tuning
The process of further training a pre-trained model on a specific dataset to improve its performance on a particular task or domain. This is more resource-efficient than training from scratch.

## Prompt Engineering
The practice of crafting effective prompts to get the best results from an LLM. Techniques include few-shot prompting, chain-of-thought reasoning, and system prompts.

## Transformer Architecture
The neural network architecture behind modern LLMs. It uses self-attention mechanisms to process sequences of tokens in parallel, enabling it to capture long-range dependencies in text.

## Tokenization
The process of breaking text into smaller units called tokens. Tokens can be words, subwords, or characters. Most LLMs use subword tokenization (e.g., BPE — Byte Pair Encoding).

## Temperature
A parameter that controls the randomness of LLM output. Lower values (e.g., 0.1) produce more deterministic responses, while higher values (e.g., 0.9) produce more creative but potentially less accurate ones.

## Hallucination
When an LLM generates information that is factually incorrect or not grounded in the provided context. RAG helps reduce hallucinations by providing relevant source material.

## Cosine Similarity
A metric used to measure how similar two vectors are. It calculates the cosine of the angle between them. A value of 1 means identical direction, 0 means orthogonal, and -1 means opposite.
