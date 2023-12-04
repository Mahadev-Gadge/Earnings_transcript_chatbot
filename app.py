import streamlit as st
import openai
import time
import os
#from earnings_transcript_scraper import data_scraper

# Assistant title.
st.title("""**Earnings transcripts assistant**""")

st.markdown(""" This assistant helps to answer user queries related to 3M company historical earnings transcript. """)

st.sidebar.subheader("**User inputs:**")

#Earnings_articles_links=data_scraper.get_earnings_transcripts(ticker_slug=ticker_slug, page_number=10)

# OpenAI assistant 
def earnings_transcript_assistant():
       
    #uploaded_file=st.sidebar.file_uploader(":blue[**Choose a transcript**]")
    #if uploaded_file is not None:
    ticker_slug=st.sidebar.text_input("**1. Enter company code:**")
    time.sleep(0.5)
    year=st.sidebar.slider("**2. Which year transcript are you interested in:**", 2005, 2023, 2023)
    time.sleep(0.5)
    quarter=st.sidebar.selectbox("**3. Which quarter transcript are you interested in:**", ('Q1','Q2','Q3','Q4'))

    if st.sidebar.button("Submit"):
        filename=ticker_slug+'-'+quarter+'-'+str(year)+'-'+"earnings_transcript.txt"
        st.write("Upon considering your inputs retrieving file from database and found filename is:", filename)
        with open(filename, 'r') as f:
            text_contents=f.read()
            st.download_button('Download transcript', text_contents)

        if 'client' not in st.session_state:
            
            st.session_state.client = openai.OpenAI(api_key=st.secrets['api_key']) 

            st.session_state.assistant = st.session_state.client.beta.assistants.create(name="Finance Assistant", instructions="You are a finance support chatbot. Use knowledge from provided file to answer to user queries.", model="gpt-4-1106-preview", tools=[{"type": "retrieval"}])
        else:
             st.write("Client already exists")
               
        st.session_state.thread = st.session_state.client.beta.threads.create()

        st.session_state.file = st.session_state.client.files.create(file=open(filename, "rb"), purpose='assistants')
        
        st.sidebar.write("Requested file id is: ", st.session_state.file.id)
        st.session_state.assistant =st.session_state.client.beta.assistants.update(assistant_id=st.session_state.assistant.id, file_ids=[st.session_state.file.id])
               
        content = st.text_input("Ask you question","Which quarter and year transcript is this belongs to?")
               
        message = st.session_state.client.beta.threads.messages.create(thread_id=st.session_state.thread.id, role="user", content=content)
        run = st.session_state.client.beta.threads.runs.create(thread_id=st.session_state.thread.id, assistant_id=st.session_state.assistant.id)
        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != 'completed':
              time.sleep(1)
              run = st.session_state.client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=run.id)
        # Retrieve messages added by the assistant
        messages = st.session_state.client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
        for msg in messages.data:
              role = msg.role
              content = msg.content[0].text.value
              st.write(f"{role.capitalize()}: {content}")
    else:
        st.write("Please upload transcript.")
           
    
earnings_transcript_assistant()
