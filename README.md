# College-Guidance-Counsellor-Chatbot

A conversational chatbot system to assist students in college/career guidance — helping them explore university options, understand admission criteria, and receive personalised recommendations.

## Table of Contents
- [Features](#features)  
- [Architecture / How it works](#architecture--how-it-works)  
- [Usage / Getting Started](#usage--getting-started)  


## Features
- Conversational chat interface (via notebook or script) that takes user input and responds with guidance.  
- A module (`scrape.py`) to pull in university/college data from web sources.  
- A retrieval-augmented generation module (`RAG.py`) to use the scraped data to form answers.  
- A utility (`get_top_uni.py`) to generate a list of top universities based on criteria.  
- Use of the Jupyter notebook `chatbot.ipynb` to demonstrate sample conversations and workflows.

## Architecture / How it works
1. **Data Acquisition** — The `scrape.py` script scrapes college/university information (e.g., admission criteria, courses offered, geographical regions).  
2. **Indexing & Retrieval** — The `RAG.py` module creates or utilises an index of that data (for example using embeddings or vector stores) so that relevant sections can be retrieved in response to user queries.  
3. **Chat Interface** — The user interacts via the `chatbot.ipynb` notebook (or could be adapted as a script) where they type questions and the system uses retrieval + generation to craft responses.  
4. **Recommendation / Top-University Logic** — The `get_top_uni.py` uses scraped data + simple ranking criteria to output a curated list of top universities for given parameters (region, field, fee bracket, etc.).  
5. **Response Generation** — Following retrieval of relevant context, the system may use a language model or prompt‐based generation to respond in safe, coherent, domain-relevant language.

## Usage / Getting Started
1. Clone this repository  
   ```bash
   git clone https://github.com/MukundIyer21/College-guidance-counsellor-chatbot.git
   cd College-guidance-counsellor-chatbot

