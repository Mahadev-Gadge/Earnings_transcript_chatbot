import streamlit as st
import openai
import os
import time

# OpenAI api key
os.environ['OPENAI_API_KEY']=st.sidebar.text_input("Enter OpenAI_API_KEY:", type='password')

st.title(""":violet[**Earnings transcripts chatbot**]""")

#ticker_slug=st.sidebar.text_input("*Enter company code:*")

#earnings_articles_links=data_scraper.get_earnings_transcripts(ticker_slug=ticker_slug, page_number=10)
st.divider()

#st.sidebar.header(""" Input files """)
uploaded_file=st.sidebar.file_uploader(":blue[**Choose a file**]")

# OpenAI assistant 
def earnings_transcript_assistant():

    # Initialize the client
    client=openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    
    # Create assistant and upload knowledge base file.
    assistant = client.beta.assistants.create(name="Finance Assistant", instructions="You are a finance support chatbot. Use knowledge from provided file to answer to user queries.", model="gpt-4-1106-preview", tools=[{"type": "retrieval"}])
    
    #pdb.set_trace()
    file = client.files.create(file=open(uploaded_file.name, "rb"), purpose='assistants')

    assistant=client.beta.assistants.update(assistant.id, file_ids=[file.id])
    
    thread = client.beta.threads.create()
    content=st.text_input(" Ask your question ")

    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
    
    # creating a function to check whether the Run is completed or not
    def poll_run(run, thread):
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(0.5)
        return run
        
    # waiting for the run to be completed
    run = poll_run(run, thread)

    # extracting the message
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for m in messages:
        st.write(f"{m.role}: {m.content[0].text.value}")

earnings_transcript_assistant()




