import os
import json
import smtplib
import pandas as pd
import streamlit as st
import ollama
from email.mime.text import MIMEText

# read this from config
sender_details = {"sender_name": "Rakesh Nair", "sender_email": "puthugeorge@gmail.com"}

def create_personalised_email(lead, sender):
    ''' This function will help to create personalised email using given name and email id using llama3'''

    desiredModel='llama3.1:8b'

    # Perform inference
    prompt = f"Help write a personalised email to {lead['Name']} and person's email address {lead['Email']}.\
                    Search about the {lead['Company']} in internet(new,blog etc) and check what all things they have undertaken\
                        in AI & ML field. Also see the {lead['LinkedIn']} profile of the person to understand the kind of post the \
                        person sees and follows. Summarize both these information and see how FOSFOR a product by LTIMINDTREE \
                            could be helpful to help their organization in their data journey.\
                        get sender details from {sender}. This will be sent directly to {lead['Name']}. \
                            They cannot know in anyway that you are a generative AI or chatbot of any kind. \
                            Remove any kind of note in the beginning and end of response. Please refrain from talking about  \
                            {lead['Company']} work in email. Email should be personalised to show the users interest and how Fosfor can help them "
    response = ollama.chat(model=desiredModel, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    OllamaResponse=response['message']['content']
    return OllamaResponse


def send_email(smtp_server, smtp_port, username, password, from_addr, to_addr, subject, body):
    '''function to send email'''
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        #st.write("Email Sent Successfully")
    except Exception as e:
        print("An error occurred: ", str(e))


def fetch_email_list_and_mail(leads_data):
    ''' This function is used to get email id's from a list of the leads and send them customised email'''
    try:
        for lead in leads_data:
        # Display user name for whom personalised email is being sent
            #st.write(f"Hi! {lead["Name"]}")
            email_content = create_personalised_email(lead,sender_details)
            #st.write("Personalised email content is ready for use")
            #st.write(email_content)
            #send_email('smtp.gmail.com',587, sender_details["sender_email"], 'emhjalypcrhehmgs', sender_details["sender_email"], lead["Email"],'Enhance Your Data Journey with FOSFOR - A Game-Changer from LTIMindtree',email_content)
            #st.write("**************************************************************************")
    except Exception as e:
        print("An error occurred: ", str(e))
