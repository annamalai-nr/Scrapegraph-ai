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
DEFAULT_PROMPT = '''Extract all the content from the webpage without missing a single word.  
1. Since there may be a large amount of text, divide it into chunks. Each chunk should be semantically relevant (for example, a paragraph or a group of sentences that discuss a single topic). Each chunk must contain at least 3 sentences.
2. For each chunk, provide the following metadata:
    - Entities mentioned in the chunk  
    - Topics discussed in the chunk  
    - Sentiment of the chunk (Positive, Negative, or Neutral)  
    - Keywords to improve the chunk's searchability  
    - Search queries that the chunk can answer  
    - If the chunk contains any images or tables, provide a detailed description of them  
    - A contextual summary that situates this chunk within the overall document/webpage for the purposes of enhancing search retrieval.

3. Return everything in JSON format according to the following schema:

    {
      "chunks": [
        {
          "text": "...",
          "metadata": {
            "entities": ["...", "..."],
            "topics": ["...", "..."],
            "sentiment": "...",
            "keywords": ["...", "..."],
            "search_queries": ["...", "..."],
            "image_narration": "...",
            "table_narration": "...",
            "summary": "..."
          }
        }
      ]
    }

4. Only return the JSON. Do not include any other text, comments, or symbols (such as backticks).
'''

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