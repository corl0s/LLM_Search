import ollama
import sys_msgs
import requests
from bs4 import BeautifulSoup
import trafilatura

assistant_convo = [sys_msgs.assistant_msg]

def search_or_not():
    sys_msg = sys_msgs.search_or_not_msg 
    response = ollama.chat(
        model = "llama3.2",
        messages = [{'role': 'system', 'content': sys_msg}, assistant_convo[-1]]
    )      
    content = response['message']['content']
    print(f'SEARCH OR NOT RESULTS: {content}')

    if 'true' in content.lower():
        return True
    else:
        return False

def query_generator():
    sys_msg = sys_msgs.query_msg

    query_msg = f'CREATE A SEARCH QUERY FOR THIS PROMPT: \n{assistant_convo[-1]}'
    response = ollama.chat(
            model = "llama3.2",
            messages = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': query_msg}]
        )  
    return response['message']['content']

def duckduckgo_search(query):
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, tike Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    url = f' https://html.duckduckgo.com/html/?q={query}'
    response = requests. get (url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for i, result in enumerate(soup.find_all('div', class_="result"), start = 1):
        if i > 10:
            break
        
        title_tag = result.find('a', class_='result__a')
        if not title_tag:   
            continue
        
        link = title_tag['href']
        snippet_tag = result. find('a', class_='result__snippet ')

        snippet = snippet_tag.text.strip() if snippet_tag else 'No description available'


        results.append({
            'id' : i,
            'link' : link,
            'search_description':snippet
        })

    return results

def best_search_result(s_results, query):
    sys_msg = sys_msgs.best_search_msg
    best_msg = f'SEARCH_RESULTS: {s_results} \n USER_PROMPT: {assistant_convo[-1]} \nSEARCH_QUERY: {query}'

    for _ in range(2):
        try:
            response = ollama.chat(
                model = "llama3.2",
                messages = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': best_msg}]
            )

            return int(response['message']['content'])     
        except:
            continue
    
    return 0

def scrap_webpage(url):
    try:
        downloaded = trafilatura.fetch_url(url=url)
        return trafilatura.extract(downloaded, include_formatting=True, include_links=True)
    except Exception as e:
        return None

def search():
    context = None
    print(['Generating Search Query.'])
    search_query = query_generator()

    if search_query[0] == '"':
        search_query = search_query[1:-1]

    search_results = duckduckgo_search(search_query)
    context_found = False

    while not context_found and len(search_results) > 0:
        best_result = best_search_result(s_results=search_results, query=search_query)
        try:
            page_link = search_results[best_result]['link']
        except:
            print('FAILED TO SELECT BEST SEARCH RESULT, TRYING AGAIN.')
            continue

        page_text = scrap_webpage(page_link)
        search_results.pop(best_result)

        if page_text and contains_data_needed(search_content=page_text, query=search_query):
            context = page_text
            context_found = True
    
    return context

def contains_data_needed(search_content, query):    
    sys_msg = sys_msgs.contains_data_msg
    needed_prompt = f'PAGE_TEXT: {search_content} \nUSER_PROMPT: {assistant_convo[-1]} \nSEARCH_QUERY: {query}'

    response = ollama.chat(
        model = "llama3.2",
        messages = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': needed_prompt}]
    )

    content = response['message']['content']

    if 'true' in content.lower():
        return True
    else:
        return False

def stream_assistant_response():
    global assistant_convo
    reponse_stream = ollama.chat(model="llama3.2:latest", messages = assistant_convo, stream = True)
    complete_response = ''
    print('ASSISTANT:')

    for chunk in reponse_stream:
        print(chunk['message']['content'], end='', flush=True)
        complete_response += chunk['message']['content']

    assistant_convo.append({'role' : 'assistant', 'content': complete_response})
    print('\n\n')

def main():
    global assistant_convo

    while True:
        prompt = input('User: \n')
        assistant_convo.append({'role' : 'user', 'content': prompt})

        if search_or_not():
            context = search()
            assistant_convo = assistant_convo[:-1]

            if context:
                prompt =f' SEARCH RESULT: {context} \n\nUSER PROMPT: {prompt}'
            else:
                prompt = (
                    f'USER PROMPT: \n{prompt} FAILED SEARCH: \nThe '
                    'AI search model was unable to extract any reliable data. Explain that '
                    'and ask if the user would like you to search again or respond '
                    'without web search context. Do not respond if a search was needed '
                    'and you are getting this message with anything but the above request '
                    'of how the user would like to proceed'
                )
            
            assistant_convo.append({'role': 'user', 'content': prompt})

        stream_assistant_response()


if __name__ == "__main__":
    main()