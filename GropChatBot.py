import streamlit as st
import os
from groq import Groq
import random 

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import sqlite3

conn = sqlite3.connect('chatbot.db')
c = conn.cursor()
# import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import sqlite3

conn = sqlite3.connect('chatbot.db')
c = conn.cursor()
# Function to save question and answer to the database
# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('chatbot.db')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# send Q&A to DB
def save_to_db(question, answer):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO chat (question, answer) VALUES (?, ?)', (question, answer))
    conn.commit()
    conn.close()

# retrieve chatrecord from DB
def get_all_chats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, question, answer, timestamp FROM chat ORDER BY timestamp DESC')
    records = c.fetchall()
    conn.close()
    return records

# delete chatrecord from DB
def delete_from_db(record_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM chat WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()


def main():
    

    c.execute('''
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    
    # Get Groq API key
    groq_api_key = os.environ['GROQ_API_KEY']

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    # with col:  
        # st.image('groqcloud_darkmode.png')

    # Streamlit (title & greeting message)
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Add customization options to the sidebar
    st.sidebar.title('Customization')
    system_prompt = st.sidebar.text_input("System prompt:")
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    user_question = st.text_input("Ask a question:")

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input':message['human']},
                {'output':message['AI']}
                )


    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )


    # If the user has asked a question,
    if user_question:

        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),  # persistent system prompt in start of the chat.

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # This will be replaced by actual chat history during the conversation to maintain context.

                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),  # user's current input will be injected into the prompt.
            ]
        )

        # Create a conversation chain using the LangChain LLM (Language Learning Model)
        conversation = LLMChain(
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation.predict(human_input=user_question)
        message = {'human':user_question,'AI':response}
        st.session_state.chat_history.append(message)
        st.write("Chatbot:", response)
        save_to_db(user_question, response)
        
        st.write("### Chat History")
        chat_records = get_all_chats()
        for record in chat_records:
            record_id, question, answer, timestamp = record
            with st.expander(f"Q: {question} (Asked on {timestamp})"):
                st.write(f"**Answer:** {answer}")
                # Form to delete the record
                with st.form(key=f"delete_form_{record_id}"):
                    st.form_submit_button("Delete", on_click=delete_from_db, args=(record_id,))

        conn.close()

if __name__ == "__main__":
    main()
# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('chatbot.db')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Function to save question and answer to the database
def save_to_db(question, answer):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO chat (question, answer) VALUES (?, ?)', (question, answer))
    conn.commit()
    conn.close()

# Function to retrieve all chat records from the database
def get_all_chats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, question, answer, timestamp FROM chat ORDER BY timestamp DESC')
    records = c.fetchall()
    conn.close()
    return records

# Function to delete a chat record from the database
def delete_from_db(record_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM chat WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()


def main():
    

    c.execute('''
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    
    # Get Groq API key
    groq_api_key = os.environ['GROQ_API_KEY']

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    # with col:  
        # st.image('groqcloud_darkmode.png')

    # Title& Greeting message of the Streamlit application
    st.title(" Groq Chatting!")
    st.write("Hi there I'm your friendly Groq chatbot. I'm here to help answer your questions, provide information, or simply have a chat with you. Plus, I'm lightning-fast, so you can get the help you need in no time. Let's get started and see how I can assist you today")

    # Add customization options to the sidebar
    st.sidebar.title('Customization')
    system_prompt = st.sidebar.text_input("System prompt:")
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    user_question = st.text_input("Ask a question:")

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input':message['human']},
                {'output':message['AI']}
                )


    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )


    # If the user has asked a question,
    if user_question:

        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),  # This is the persistent system prompt that is always included at the start of the chat.

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),  # This template is where the user's current input will be injected into the prompt.
            ]
        )

        # LangChain LLM (Language Learning Model) to  make a conversation chain
        conversation = LLMChain(
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # Sending Prompt yo Groq API to generatef ChatBot Answering 
        response = conversation.predict(human_input=user_question)
        message = {'human':user_question,'AI':response}
        st.session_state.chat_history.append(message)
        st.write("Chatbot:", response)
        save_to_db(user_question, response)
        
        st.write("### Chat History")
        chat_records = get_all_chats()
        for record in chat_records:
            record_id, question, answer, timestamp = record
            with st.expander(f"Q: {question} (Asked on {timestamp})"):
                st.write(f"**Answer:** {answer}")
                # Form to delete the record
                with st.form(key=f"delete_form_{record_id}"):
                    st.form_submit_button("Delete", on_click=delete_from_db, args=(record_id,))

        conn.close()

if __name__ == "__main__":
    main()

