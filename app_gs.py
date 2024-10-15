import os
import streamlit as st
import pandas as pd
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from utils_localllama import *
from utils_perplexity import *

# Streamlit App
# Set page config to use full screen
st.set_page_config(layout="wide")
# Create pages
page = st.sidebar.selectbox("Choose a page", ["About Us", "Genzoic's SDR AI"])

# Section 1: About Us
if page == "About Us":
    st.title("Welcome To Genzoic")
    st.header("About Us")
    with st.expander("Read More"):
        company_description = """
                                Genzoic revolutionizes productivity by crafting cutting-edge generative AI assistants 
                                that automate mundane daily tasks.

                                Leveraging expertise in AI innovation, we offer: \n
                                    1. Pre-built AI assistants for common tasks
                                    2. Custom AI solutions tailored to specific needs

                                Our AI assistants seamlessly integrate into your workflow, freeing you to focus 
                                on high-value tasks.

                                Experience the future of work with X Genesis AI.
                            """
        st.write(company_description)
    st.image("AI-assistant.jpg", use_column_width=True)
    st.subheader("Contact Us:")
    st.write("Email: [genzoic@example.com](mailto:genzoic@example.com)")
    st.write("Phone: +1-123-456-7890")
    st.write("Address: 123 Main Street, ABC, USA 12345")

# Section 2: Lead Upload and Preview
elif page == "Genzoic's SDR AI":
    st.title("Revolutionize Your Sales Workflow using - SDR AI Assistant")
    st.write("Provide the Lead details from google sheet")
    # Google Sheets API settings
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # Initialize session state
    if 'sheet_url' not in st.session_state:
        st.session_state.sheet_url = ''
    if 'spreadsheet_id' not in st.session_state:
        st.session_state.spreadsheet_id = ''
    if 'creds' not in st.session_state:
        st.session_state.creds = None
    if 'service' not in st.session_state:
        st.session_state.service = None
    if 'preview' not in st.session_state:
        st.session_state.preview = False
    if 'records' not in st.session_state:
        st.session_state.records = []
    if 'num_records' not in st.session_state:
        st.session_state.num_records = 5
    if 'follow_up' not in st.session_state:
        st.session_state.follow_up = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'header' not in st.session_state:
        st.session_state.header = None

    # Initialize empty list to store lead data
    st.session_state.records = []

    # Extract spreadsheet ID from URL
    def get_spreadsheet_id(url):
        url_parts = url.split("/")
        return url_parts[5]

    # Authenticate with Google Sheets
    def authenticate():
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds


    # Display sheet records preview
    def display_sheet_records(service, spreadsheet_id):
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range="A:Z"
        ).execute()
        values = result.get('values', [])
        # Initialize max columns
        max_cols = 0
        # Find max columns
        for row in values:
            max_cols = max(max_cols, len(row))
        
        # Pad rows with empty strings
        for i, row in enumerate(values):
            values[i] += [''] * (max_cols - len(row))
        
        # Replace empty strings with None
        values = [[cell if cell != '' else None for cell in row] for row in values]
        # Check if values are available
        if values:
            # Set headers as the first row and data as the remaining rows
            headers = values[0]
            data = [[cell if cell else None for cell in row] for row in values[1:]]
            # Replace empty strings with None
            data = [[None if cell == '' else cell for cell in row] for row in data]
            df = pd.DataFrame(data, columns=headers)
        else:
            df = pd.DataFrame()
        return df
    
    # Get Google Sheet URL from user
    url_key = 'sheet_url'
    st.session_state['url_key'] = st.text_input("Enter Google Sheet URL",key=url_key)

    # Clear existing data and write entire DataFrame
    def clear_and_write_data_to_sheet(service, spreadsheet_id, range_name, df):
        clear_body = {
                'range': f"{range_name[0]}2:{range_name[-1]}{df.shape[0]+1}"  # Start from row 2
            }
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            body=clear_body,
            range=range_name
        ).execute()

        # Write entire DataFrame (including headers and index)
        write_body = {
            'values': [[df.index.name] + df.columns.values.tolist()] +  # Header row with index name
                    [[i] + row for i, row in zip(df.index, df.values.tolist())]  # Data rows with index
        }
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=write_body
        ).execute()
        st.write(f"Data updated.")

    #submit and clear button logic
    col1, col2 = st.columns(2)
    with col1:
            # Submit button
        if st.button("Submit"):
            if st.session_state[url_key]:
                st.session_state.spreadsheet_id = get_spreadsheet_id(st.session_state['url_key'])
                st.session_state.creds = authenticate()
                st.session_state.service = build('sheets', 'v4', credentials=st.session_state.creds)
                st.session_state.df = display_sheet_records(st.session_state.service, st.session_state.spreadsheet_id)
                st.session_state.preview = True
                st.session_state.follow_up = True
    with col2:
        if st.button("Clear"):
            st.session_state['url_key'] = ''
            st.session_state.preview = False
            st.session_state.df = []
            st.session_state.follow_up = False
    
    # Preview section
    if st.session_state.preview:
        with st.expander("Preview"):
            selected_records = st.selectbox("Select number of records to preview", options=["10", "50", "100", "All"],key="num_records")
            if selected_records == "All":
                preview_df = st.session_state.df
            else:
                selected_records = int(selected_records)
                preview_df = st.session_state.df.head(selected_records)
            # Display preview
            st.subheader("Preview")
            st.dataframe(preview_df)
    

    #Follow-up Details section
    if st.session_state.follow_up:
        with st.expander("Follow Up"):
            # Select rows
            selected_row = st.selectbox("Select Lead:", st.session_state.df.loc[st.session_state.df.index]['Name'])
            selected_df = st.session_state.df.loc[st.session_state.df['Name']==selected_row]
            st.dataframe(selected_df)
            st.write("\n")
            st.write("Fetch Latest work done in the field of AI/ML by ")
            # Button container
            col1, col2 = st.columns(2)
            with col1:
                fetch_company_button = st.button("Company")
            with col2:
                fetch_user_button = st.button("User")
            for index, row in selected_df.iterrows():
                # Append lead data to session state
                st.session_state.records = []
                st.session_state.records.append({
                    "Name": row[0],
                    "Email": row[1],
                    "Company": row[2],
                    "LinkedIn": row[3],
                    "Context": row[4],
                    "First_Follow_Up": row[5],
                    "Email_status": row[6],
                    "Second_Follow_up": row[7]
                })
            # Button actions
            if fetch_company_button:
                for lead in st.session_state.records:
                    st.write("Using perplexity to fetch from internet the latest information.......")
                    prompt = f"Search about the {lead['Company']} in internet(new,blog etc) and check what all latest things they have undertaken\
                            in AI & ML field. Generate a summary in 200 words to be shown to a sales person. \
                            The summary should be crisp and relevant"
                    response = provide_online_checks(prompt)
                    st.write(response)
            if fetch_user_button:
                for lead in st.session_state.records:
                    st.write("Using perplexity to fetch lead informtion from linkedin.......")
                    prompt = f"Search about {lead['Name']} in his {lead['LinkedIn']} profile and try to see what kind of post the user likes and posts\
                    Find if user is interested in AI/ML work and has done something in it. Summarise the information in a paragraph."
                    response = provide_online_checks(prompt)
                    st.write(response)

            #======================================================================
            #st.write(st.session_state.df)

            # st.session_state.records = fetch_email_list_and_mail(st.session_state.records)
            # st.session_state.df = pd.DataFrame(st.session_state.records)
            # # Clear existing data and write entire DataFrame
            # st.session_state.service = build('sheets', 'v4', credentials=st.session_state.creds)
            # range_name = 'A:Z'  # Update range as needed
            # clear_and_write_data_to_sheet(st.session_state.service, st.session_state.spreadsheet_id, range_name, st.session_state.df)
            
            