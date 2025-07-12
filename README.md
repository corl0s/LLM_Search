# 🔍 Web-Augmented AI Assistant

This project is an **LLM-powered AI assistant** enhanced with **live web search capabilities**. It automatically determines whether a user query requires real-time data, performs web search using DuckDuckGo, extracts relevant content from search results, and uses it to generate accurate and up-to-date responses.

---

## Features

- Smart Assistant: Uses LLaMA3.2 to chat with users in a helpful and context-aware manner.
- Intelligent Web Search: Automatically decides when a query needs web search.
- Modular LLM Roles:
  - Search Decision
  - Query Generation
  - Result Ranking
  - Page Usefulness Evaluation
- Clean Scraping: Uses `trafilatura` to extract readable and relevant content from pages.
- Streaming Response: Responds in real-time using streamed output.

---

## How It Works

1. User enters a prompt.
2. The assistant decides if live search is needed.
3. If yes:
   - Generates a search query.
   - Performs a DuckDuckGo search.
   - Ranks top results.
   - Scrapes and verifies web pages.
   - If useful content found, prepends it to the prompt.
4. The assistant generates a response using context.


