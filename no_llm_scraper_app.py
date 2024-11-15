import streamlit as st
from scrapegraphai.nodes.fetch_node import FetchNode
from scrapegraphai.nodes.parse_node import ParseNode
import time
import nest_asyncio

# Enable nested event loops
nest_asyncio.apply()

def create_nodes():
    # FetchNode configuration
    fetch_node_config = {
        "headless": False,
        "verbose": True,
        "use_playwright": True,
        "playwright_options": {
            "java_script_enabled": True,
            "cookies": []
        }
    }
    
    # ParseNode configuration
    parse_node_config = {
        "verbose": True,
        "parse_html": True,
        "chunk_size": 4096,
    }
    
    # Create nodes
    fetch_node = FetchNode(
        input="url",
        output=["fetched_content"],
        node_config=fetch_node_config
    )
    
    parse_node = ParseNode(
        input="fetched_content",
        output=["parsed_content"],
        node_config=parse_node_config
    )
    
    return fetch_node, parse_node

def scrape_url(url, fetch_node, parse_node):
    timings = {}
    
    # Initialize state
    state = {"url": url}
    
    # Execute FetchNode
    fetch_start = time.time()
    state = fetch_node.execute(state)
    fetch_end = time.time()
    timings['fetch_time'] = fetch_end - fetch_start
    
    # Execute ParseNode
    parse_start = time.time()
    state = parse_node.execute(state)
    parse_end = time.time()
    timings['parse_time'] = parse_end - parse_start
    
    timings['total_time'] = timings['fetch_time'] + timings['parse_time']
    
    return state.get("parsed_content")[0], timings

def main():
    st.title("Web Content Scraper (No LLM needed)")
    
    # Initialize nodes
    fetch_node, parse_node = create_nodes()
    
    # URL input
    url = st.text_input("Enter URL to scrape:", "https://www.anthropic.com")
    
    if st.button("Scrape"):
        with st.spinner("Scraping content..."):
            try:
                # Perform scraping
                content, timings = scrape_url(url, fetch_node, parse_node)
                
                # Display content
                st.header("Scraped Content")
                st.code(content, language="text")
                
                # Display timing statistics
                st.header("Performance Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Fetch Time",
                        value=f"{timings['fetch_time']:.2f}s"
                    )
                
                with col2:
                    st.metric(
                        label="Parse Time",
                        value=f"{timings['parse_time']:.2f}s"
                    )
                
                with col3:
                    st.metric(
                        label="Total Time",
                        value=f"{timings['total_time']:.2f}s"
                    )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()