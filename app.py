import streamlit as st
import json
from scrapegraphai.graphs import SmartScraperGraph
from dotenv import load_dotenv
import os
import asyncio
import nest_asyncio

# Load environment variables
load_dotenv()

# Enable nested event loops
nest_asyncio.apply()

# Default prompt
DEFAULT_PROMPT = '''Extract all the contents from the webpage (do not miss even a single word). 
1. Since there can be large number of words/sentences, chunk them. Each chunk should be semantically relevant (example: a paragraph, a bunch of sentences that talk about one topic, etc.). Each chunk should be at least 3 sentences long.
2. For each chunk, provide the following metadata:
    a. Entities mentioned in the chunk
    b. Topics discussed in the chunk
    c. Sentiment (Positive, Negative, Neutral) of the chunk
    d. Keywords that can help better searchability of the chunk
    e. Search queries that the chunk can answer
    f. If the chunk contains any images or tables, narrate in detail about them.
    f. A contextual summary that situates this chunk within the overall document/webpage for the purposes of improving search retrieval of the chunk.
3. Return everything in JSON format. The following is the schema for the JSON:
    {
        "chunks": [{"text": "...", 
                    "metadata": {"entities": ["...", "..."], 
                                 "topics": ["...", "..."], 
                                 "sentiment": "...", 
                                 "keywords": ["...", "..."], 
                                 "search_queries": ["...", "..."],
                                 "image_narration": "...",
                                 "table_narration": "...",
                                 "summary": "..."}}]
    }
4. Only return the JSON. Do not include any other text or comments or symbols (example: backticks(`))
'''

# ... previous imports and DEFAULT_PROMPT remain the same ...

def main():
    st.title("Web Content Scraper")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("OpenAI API Key:", type="password")
        model = st.selectbox("Select Model:", ["openai/gpt-4o-mini", "openai/gpt-4o"])
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    
    # Main content
    url = st.text_input("Enter URL to scrape:", "https://www.anthropic.com/news/contextual-retrieval")
    prompt = st.text_area("Customize the prompt:", DEFAULT_PROMPT, height=300)
    
    if st.button("Scrape"):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar")
            return
            
        # Configuration
        graph_config = {
            "llm": {
                "api_key": api_key,
                "model": model,
            },
            "verbose": True,
            "headless": False,
            "temperature": temperature
        }
        
        # Create and run the scraper
        with st.spinner("Scraping and analyzing content..."):
            try:
                smart_scraper_graph = SmartScraperGraph(
                    prompt=prompt,
                    source=url,
                    config=graph_config
                )
                
                # Run the scraper synchronously
                result = smart_scraper_graph.run()
                
                # Display results
                if isinstance(result, dict) and 'chunks' in result:
                    for i, chunk in enumerate(result['chunks'], 1):
                        with st.expander(f"Chunk {i}: {chunk['metadata']['summary']}", expanded=False):
                            st.write("**Full Text:**")
                            st.write(chunk['text'])
                            st.write("**Metadata:**")
                            metadata = chunk['metadata']
                            st.json(metadata)
                else:
                    st.error("Unexpected response format")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()