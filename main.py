import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
from datetime import datetime


#caching
# import json
# import os

# CACHE_FILE = "cache.json"

# # Load cache
# if os.path.exists(CACHE_FILE):
#     with open(CACHE_FILE, "r") as f:
#         cache = json.load(f)
# else:
#     cache = {}

# def save_cache():
#     with open(CACHE_FILE, "w") as f:
#         json.dump(cache, f, indent=2)



def get_search_results(topic, max_results=10):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(topic, max_results=max_results):
            results.append({"title": r["title"], "link": r["href"]})
    return results

def get_text_from_url(url):
    try:
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs[:5]])
    except:
        return ""

def rank_results_tfidf(topic, results):
    texts = [get_text_from_url(res['link']) for res in results]
    
    valid_results = []
    content_texts = []
    
    for res, text in zip(results, texts):
        if text.strip():
            res['summary'] = text[:300]
            valid_results.append(res)
            content_texts.append(text)

    if not content_texts:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([topic] + content_texts)

    topic_vec = vectors[0]
    content_vecs = vectors[1:]

    similarities = cosine_similarity(topic_vec, content_vecs).flatten()

    for i, score in enumerate(similarities):
        valid_results[i]['score'] = score

    return sorted(valid_results, key=lambda x: x['score'], reverse=True)

def get_images(topic):
    with DDGS() as ddgs:
        return [{"image": r["image"], "title": r["title"]} for r in ddgs.images(topic, max_results=7)]

def get_videos(topic, max_results=7):
    with DDGS() as ddgs:
        results = ddgs.text(f"{topic} site:youtube.com", max_results=max_results)

        videos = []
        for r in results:
            title = r.get("title", "")
            description = r.get("body", "")
            url = r.get("href", "")
            upload_time = ""

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                date_tag = soup.find("meta", itemprop="uploadDate")
                if date_tag:
                    upload_time = date_tag["content"]
            except Exception as e:
                print(f"Error fetching upload date: {e}")

            videos.append({
                "title": title,
                "href": url,
                "body": description,
                "upload_time": upload_time
            })

        return videos

def get_links(topic):
    time.sleep(2)
    results = get_search_results(topic)
    return [r['link'] for r in results]

def get_text(topic):
    results = get_search_results(topic)
    ranked = rank_results_tfidf(topic, results)
    return ranked

def get_all_resources(topic):
    # if topic in cache:
    #     print(f"Using cached result for: {topic}")
    #     return cache[topic]
    # print(f"🔍 Fetching new results for: {topic}")
    
    data = {
        "topic": topic, 
        "links": get_links(topic),
        "articles": get_text(topic),
        "images": get_images(topic),
        "videos": get_videos(topic),
    }
    # cache[topic] = data
    # save_cache()
    return data


resources = get_all_resources("Learning habits")

# print("\n******* ARTICLES *******\n")
# for article in resources["articles"]:
#     print(f"\n🔗 {article['title']} ({article['score']:.2f})")
#     print(f"URL: {article['link']}")
#     print(f"Summary: {article['summary']}")

# print("\n******* IMAGES *******\n")
# for img in resources['images']:
#     print(f"\nTitle: {img['title']}")
#     print(f"URL: {img['image']}")

# print("\n******* VIDEOS *******\n")
# for video in resources['videos']:
#     print(f"\nTitle: {video['title']}")
#     print(f"URL: {video['href']}")
#     print(f"Desc: {video['body']}")
#     print(f"Upload Time: {video['upload_time']}")