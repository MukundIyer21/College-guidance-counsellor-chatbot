import os
from dotenv import load_dotenv
import streamlit as st
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import history_aware_retriever, retrieval
from langchain_core.messages import HumanMessage, AIMessage
import uuid

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="Masters Guidance Counsellor",
    page_icon="🎓",
    layout="wide"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("Masters College Guidance Counsellor 🎓")
st.markdown("*Get personalized guidance for pursuing your Master's degree abroad*")

st.sidebar.header("Student Information")

student_name = st.sidebar.text_input("Your Name", placeholder="Enter your name")


fields_of_interest = [
    "Select Field",
    "Artificial Intelligence",
    "Data Science",
    "Computer Science",
    "Software Engineering",
    "Machine Learning",
    "Cybersecurity",
    "Information Technology",
    "Business Analytics",
    "Finance",
    "Management",
    "Marketing",
    "Biotechnology",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Civil Engineering",
    "Environmental Science",
    "Psychology",
    "Healthcare Management",
    "Other"
]

field_interest = st.sidebar.selectbox(
    "Field of Interest",
    options=fields_of_interest
)


countries = [
    "United States",
    "UK",
    "Canada",
    "Germany",
    "Australia",
    "Ireland",
    "New Zealand"
]

preferred_countries = st.sidebar.multiselect(
    "Preferred Countries",
    options=countries,
    help="Select one or more countries"
)


st.sidebar.markdown("---")
budget_range = st.sidebar.select_slider(
    "Budget Range (USD/year)",
    options=["<20k", "20k-40k", "40k-60k", "60k-80k", ">80k"]
)


if st.sidebar.button("🔄 Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()


st.sidebar.markdown("---")
st.sidebar.caption(f"Session ID: {st.session_state.session_id[:8]}...")


@st.cache_resource
def initialize_vectorstore():
    persist_directory = "chroma_local_db"
    

    hf_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={"device": "cuda"},  
        encode_kwargs={"batch_size": 64, "normalize_embeddings": False}
    )
    try:
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=hf_embeddings
        )
        collection_count = vectorstore._collection.count()
        # testing if the vectorstore works
        st.sidebar.success(f"Loaded {collection_count} documents from database")
        return vectorstore
    except Exception as e:
        st.error(f"Error loading vectorstore: {str(e)}")
        st.info("💡 Tip: Make sure your Chroma database exists at 'chroma_local_db' and was created with the same embedding settings")
        st.stop()

@st.cache_resource
def initialize_llm():
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY is not set. Please set it in your .env file.")
        st.stop()
    
    model_name = "meta-llama/llama-4-maverick-17b-128e-instruct"  
    llm = ChatGroq(model_name=model_name, temperature=0.7, groq_api_key=GROQ_API_KEY)
    return llm


def build_user_context():
    context_parts = []
    
    if student_name:
        context_parts.append(f"Student Name: {student_name}")
    
    if field_interest and field_interest != "Select Field":
        context_parts.append(f"Field of Interest: {field_interest}")
    
    if preferred_countries:
        countries_str = ", ".join(preferred_countries)
        context_parts.append(f"Preferred Countries: {countries_str}")
    
    if budget_range:
        context_parts.append(f"Budget Range: {budget_range} per year")
    
    if context_parts:
        return "\n".join(context_parts)
    return "No specific preferences provided"


@st.cache_resource
def create_rag_chain(_llm, _retriever):
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever_var = history_aware_retriever.create_history_aware_retriever(
        _llm, _retriever, contextualize_q_prompt
    )

    system_prompt = (
        "You are an experienced Indian guidance counsellor specializing in helping students pursue Master's degrees abroad. "
        "Your role is to provide comprehensive, personalized advice based on the student's profile and preferences.\n\n"
        "Student Profile:\n{user_context}\n\n"
        "Use the following retrieved context to answer the student's question:\n{context}\n\n"
        "Guidelines:\n"
        "- Provide specific, actionable advice tailored to the student's field and country preferences\n"
        "- Consider budget constraints when making recommendations\n"
        "- Mention relevant universities, programs, scholarships, and application requirements\n"
        "- Be encouraging and supportive while being realistic\n"
        "- If you don't know something, admit it honestly\n"
        "- Keep responses clear and well-structured\n"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    question_answer_chain = create_stuff_documents_chain(_llm, qa_prompt)
    
    rag_chain = retrieval.create_retrieval_chain(history_aware_retriever_var, question_answer_chain)
    
    return rag_chain


try:
    vectorstore = initialize_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = initialize_llm()
    rag_chain = create_rag_chain(llm, retriever)
except Exception as e:
    st.error(f"Error initializing the application: {str(e)}")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if len(st.session_state.messages) == 0:
    st.markdown("### Suggested Questions:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Best universities for my field"):
            suggested_query = f"What are the best universities for {field_interest if field_interest != 'Select Field' else 'my field'} in {', '.join(preferred_countries) if preferred_countries else 'popular countries'}?"
            st.session_state.suggested_query = suggested_query
            st.rerun()
        
        if st.button("Scholarship opportunities"):
            st.session_state.suggested_query = "What scholarship opportunities are available for Indian students?"
            st.rerun()
    
    with col2:
        if st.button("Application requirements"):
            st.session_state.suggested_query = "What are the typical application requirements for Master's programs?"
            st.rerun()
        
        if st.button("Application timeline"):
            st.session_state.suggested_query = "What is the typical application timeline for Master's programs?"
            st.rerun()


if "suggested_query" in st.session_state:
    query = st.session_state.suggested_query
    del st.session_state.suggested_query
else:
    query = st.chat_input("Ask me anything about pursuing your Master's degree abroad...")


if query:

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                user_context = build_user_context()

                response = rag_chain.invoke({
                    "input": query,
                    "chat_history": st.session_state.chat_history,
                    "user_context": user_context
                })
                
                answer = response["answer"]
                

                st.markdown(answer)
                

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.chat_history.extend([
                    HumanMessage(content=query),
                    AIMessage(content=answer)
                ])
                
                
                if "context" in response and response["context"]:
                    with st.expander("View Sources"):
                        for i, doc in enumerate(response["context"][:3]):
                            st.markdown(f"**Source {i+1}:**")
                            st.markdown(doc.page_content[:300] + "...")
                            st.markdown("---")
            
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


st.markdown("---")
