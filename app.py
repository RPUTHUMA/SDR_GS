import streamlit as st
import pandas as pd

# Streamlit App

# Create pages
page = st.sidebar.selectbox("Choose a page", ["About Us", "Gensoic's SDR AI"])

# Section 1: About Us
if page == "About Us":
    st.title("Welcome To Gensoic")
    st.header("About Us")
    with st.expander("Read More"):
        company_description = """
                                Gensoic revolutionizes productivity by crafting cutting-edge generative AI assistants 
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
    st.write("Email: [gensoic@example.com](mailto:gensoic@example.com)")
    st.write("Phone: +1-123-456-7890")
    st.write("Address: 123 Main Street, ABC, USA 12345")

# Section 2: Lead Upload and Preview
elif page == "Gensoic's SDR AI":
    st.title("Revolutionize Your Sales Workflow using - SDR AI Assistant")
    st.write("Upload the Lead details")

    # Initialize session state
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
        st.session_state.df = None
        st.session_state.preview = False
        st.session_state.preview_records = "10"


    # File uploader for Google Sheet
    uploaded_file = st.file_uploader("Choose a Google Sheet (CSV or Excel)", type=['csv', 'xlsx'])

    if uploaded_file:
        # Update session state
        st.session_state.uploaded_file = uploaded_file
        if st.session_state.uploaded_file:
            st.session_state.preview = True
            # Read the uploaded file into a Pandas DataFrame
            if st.session_state.uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(st.session_state.uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                st.session_state.df = pd.read_excel(st.session_state.uploaded_file)

        # Display preview options
        if st.session_state.preview:
            with st.expander("Preview"):
                selected_records = st.selectbox("Select number of records to preview", options=["10", "50", "100", "All"],key="preview_records")
                if selected_records == "All":
                    preview_df = st.session_state.df
                else:
                    selected_records = int(selected_records)
                    preview_df = st.session_state.df.head(selected_records)
                # Display preview
                st.subheader("Preview")
                st.dataframe(preview_df)