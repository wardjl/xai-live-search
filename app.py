import streamlit as st
import requests
import json
import os
from datetime import datetime
import pytz

# Set page configuration
st.set_page_config(
    page_title="xAI Live Search",
    page_icon="🔍",
    layout="wide"
)

# App title and description
st.title("xAI Live Search API")
st.markdown("A simple interface to test the xAI Live Search API with configurable parameters.")

# Sidebar for API configuration
with st.sidebar:
    st.header("API Configuration")
    api_key = st.text_input("xAI API Key", type="password", help="Enter your xAI API key")
    api_endpoint = st.text_input("API Endpoint", value="https://api.x.ai/v1/chat/completions", 
                                help="The xAI API endpoint for chat completions")
    model = st.selectbox("Model", ["grok-3-latest", "grok-2", "grok-1"], 
                        help="Select the xAI model to use")

# Main content area
tab1, tab2, tab3 = st.tabs(["Basic Query", "Advanced Options", "API Response"])

with tab1:
    st.header("Query")
    user_message = st.text_area("Enter your message/query:", 
                               placeholder="E.g., 'Provide me a digest of world news in the last 24 hours.'"
                               , height=100)
    
    # Search mode
    search_mode = st.radio(
        "Search Mode",
        ["auto", "on", "off"],
        index=0,
        horizontal=True,
        help="'auto': Model decides whether to search, 'on': Always search, 'off': Never search"
    )

with tab2:
    st.header("Advanced Search Parameters")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date", value=None, 
                                 help="Start date for search data (ISO format YYYY-MM-DD)")
    with col2:
        to_date = st.date_input("To Date", value=None, 
                               help="End date for search data (ISO format YYYY-MM-DD)")
    
    # Return citations
    return_citations = st.checkbox("Return Citations", value=True, 
                                  help="Include source citations in the response")
    
    # Max search results
    max_results = st.slider("Maximum Search Results", min_value=1, max_value=50, value=20, 
                           help="Limit the number of data sources considered")
    
    # Data sources
    st.subheader("Data Sources")
    
    # Web source
    web_enabled = st.checkbox("Web Search", value=True)
    if web_enabled:
        web_col1, web_col2 = st.columns(2)
        with web_col1:
            web_country = st.text_input("Web Country Code", max_chars=2, 
                                       help="ISO alpha-2 country code (e.g., 'US', 'GB', 'JP')")
            web_safe_search = st.checkbox("Web Safe Search", value=True)
        with web_col2:
            web_excluded = st.text_area("Excluded Websites (Web)", 
                                       placeholder="One domain per line (e.g., wikipedia.org)", 
                                       height=100)
    
    # News source
    news_enabled = st.checkbox("News Search", value=True)
    if news_enabled:
        news_col1, news_col2 = st.columns(2)
        with news_col1:
            news_country = st.text_input("News Country Code", max_chars=2, 
                                        help="ISO alpha-2 country code (e.g., 'US', 'GB', 'JP')")
            news_safe_search = st.checkbox("News Safe Search", value=True)
        with news_col2:
            news_excluded = st.text_area("Excluded Websites (News)", 
                                        placeholder="One domain per line (e.g., bbc.co.uk)", 
                                        height=100)
    
    # X source
    x_enabled = st.checkbox("X (Twitter) Search", value=True)
    if x_enabled:
        x_handles = st.text_area("X Handles", 
                               placeholder="One handle per line (without @, e.g., grok)", 
                               height=100)
    
    # RSS source
    rss_enabled = st.checkbox("RSS Feed", value=False)
    if rss_enabled:
        rss_link = st.text_input("RSS Feed URL", 
                               placeholder="https://status.x.ai/feed.xml")

# Send button (outside tabs to always be visible)
send_col1, send_col2, send_col3 = st.columns([1, 1, 3])
with send_col1:
    send_button = st.button("Send Request", type="primary", use_container_width=True)
with send_col2:
    clear_button = st.button("Clear Results", type="secondary", use_container_width=True)

# Store API response in session state
if "api_response" not in st.session_state:
    st.session_state.api_response = None
if "request_payload" not in st.session_state:
    st.session_state.request_payload = None
if "response_time" not in st.session_state:
    st.session_state.response_time = None

if clear_button:
    st.session_state.api_response = None
    st.session_state.request_payload = None
    st.session_state.response_time = None

# Process the request when the send button is clicked
if send_button:
    if not api_key:
        st.error("Please enter your xAI API key")
    elif not user_message:
        st.error("Please enter a message/query")
    else:
        try:
            # Prepare the sources list
            sources = []
            
            if web_enabled:
                web_source = {"type": "web"}
                if web_country:
                    web_source["country"] = web_country
                if not web_safe_search:
                    web_source["safe_search"] = False
                if web_excluded:
                    excluded_websites = [site.strip() for site in web_excluded.split('\n') if site.strip()]
                    if excluded_websites:
                        web_source["excluded_websites"] = excluded_websites[:5]  # Max 5 websites
                sources.append(web_source)
            
            if news_enabled:
                news_source = {"type": "news"}
                if news_country:
                    news_source["country"] = news_country
                if not news_safe_search:
                    news_source["safe_search"] = False
                if news_excluded:
                    excluded_websites = [site.strip() for site in news_excluded.split('\n') if site.strip()]
                    if excluded_websites:
                        news_source["excluded_websites"] = excluded_websites[:5]  # Max 5 websites
                sources.append(news_source)
            
            if x_enabled:
                x_source = {"type": "x"}
                if x_handles:
                    handles = [handle.strip() for handle in x_handles.split('\n') if handle.strip()]
                    if handles:
                        x_source["x_handles"] = handles
                sources.append(x_source)
            
            if rss_enabled and rss_link:
                rss_source = {"type": "rss", "links": [rss_link]}
                sources.append(rss_source)
            
            # Prepare search parameters
            search_parameters = {"mode": search_mode}
            
            if sources:
                search_parameters["sources"] = sources
            
            if return_citations:
                search_parameters["return_citations"] = True
            
            if max_results != 20:
                search_parameters["max_search_results"] = max_results
            
            if from_date:
                search_parameters["from_date"] = from_date.strftime("%Y-%m-%d")
            
            if to_date:
                search_parameters["to_date"] = to_date.strftime("%Y-%m-%d")
            
            # Prepare the full payload
            payload = {
                "messages": [{"role": "user", "content": user_message}],
                "search_parameters": search_parameters,
                "model": model
            }
            
            # Save the payload for display
            st.session_state.request_payload = payload
            
            # Send the request to the API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            with st.spinner("Sending request to xAI API..."):
                response = requests.post(
                    api_endpoint,
                    data=json.dumps(payload),
                    headers=headers
                )
            
            # Store the response and timestamp
            st.session_state.api_response = response.json()
            st.session_state.response_time = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Switch to the API Response tab
            st.query_params.update(tab="api_response")
            
        except Exception as e:
            st.error(f"Error sending request: {str(e)}")

# Display API response in the third tab
with tab3:
    st.header("API Response")
    
    if st.session_state.api_response:
        st.success(f"Request sent successfully at {st.session_state.response_time}")
        
        # Display the request payload
        with st.expander("Request Payload"):
            st.json(st.session_state.request_payload)
        
        # Display the response
        st.subheader("Response")
        st.json(st.session_state.api_response)
        
        # Extract and display the content if available
        try:
            if "choices" in st.session_state.api_response and st.session_state.api_response["choices"]:
                content = st.session_state.api_response["choices"][0]["message"]["content"]
                st.subheader("Response Content")
                st.markdown(content)
                
                # Display citations if available
                if "citations" in st.session_state.api_response["choices"][0]["message"]:
                    citations = st.session_state.api_response["choices"][0]["message"]["citations"]
                    st.subheader("Citations")
                    for i, citation in enumerate(citations, 1):
                        st.markdown(f"{i}. [{citation}]({citation})")
        except Exception as e:
            st.error(f"Error parsing response content: {str(e)}")
            st.json(st.session_state.api_response)  # Show raw response as fallback
