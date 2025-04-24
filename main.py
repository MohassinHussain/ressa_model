import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from googlesearch import search as g_search
import joblib
import time
from datetime import datetime, timezone

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_search_results(topic, max_results=15):
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

def rank_results(topic, results):
    topic_embedding = model.encode(topic, convert_to_tensor=True)
    ranked = []

    for res in results:
        content = get_text_from_url(res['link'])
        if content:
            content_embedding = model.encode(content, convert_to_tensor=True)
            score = util.pytorch_cos_sim(topic_embedding, content_embedding).item()
            res['score'] = score
            res['summary'] = content[:300]
            ranked.append(res)

    return sorted(ranked, key=lambda x: x['score'], reverse=True)

def get_images(topic):
    with DDGS() as ddgs:
        return [{"image": r["image"], "title": r["title"]} for r in ddgs.images(topic, max_results=7)]

def get_videos(topic, max_results=5):
    with DDGS() as ddgs:
        results = ddgs.text(f"{topic} site:youtube.com", max_results=max_results)

        videos = []


        # print("Raw search results:")
        # print(results)

        for r in results:

            title = r.get("title", "")
            description = r.get("body", "")
            url = r.get("href", "")
            r.get("upload")

# Get Upload time by scraping
            upload_time = ""
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for upload date in meta tags
                date_tag = soup.find("meta", itemprop="uploadDate")
                if date_tag:
                    upload_time = date_tag["content"]  # Format: '2023-06-15'
            except Exception as e:
                print(f"Error fetching upload date: {e}")


            # Print each result for inspection
            # print(f"Result: {r}")
            # if upload_time and datetime.strptime(upload_time, '%Y-%m-%dT%H:%M:%S%z') > datetime(2024, 1, 1):
            videos.append({
                "title": title, "href": url, "body": description, "upload_time": upload_time
            })

            # Only append to videos list if the URL is a valid YouTube link
            # if title and url and "youtube.com/watch" in url:
            #     videos.append({
            #         "title": title,
            #         "description": description,
            #         "url": url
            #     })

        return videos




# def get_videos(topic, max_results=5):
#     videos = []
#     with DDGS() as ddgs:
#         for result in ddgs.videos(topic, max_results=max_results):
#             url = result.get("url", "")
#             if "youtube.com/watch" in url:
#                 videos.append({
#                     "title": result.get("title", "YouTube Video"),
#                     "description": result.get("content", ""),
#                     "url": url
#                 })
#     return videos

# def get_videos(topic, max_results=5):
#     query = f"{topic} site:youtube.com"
#     videos = []
#     try:
#         links = g_search(query)
#         for link in links:
#             if "youtube.com/watch" in link:
#                 videos.append({
#                     "title": "YouTube Video",
#                     "description": "",
#                     "url": link
#                 })
#             time.sleep(2)  # add delay to avoid 429
#     except Exception as e:
#         print("Error:", e)
#     return videos



def get_links(topic):
    results = get_search_results(topic)
    return [r['link'] for r in results]


def get_text(topic):
    results = get_search_results(topic)
    ranked = rank_results(topic, results)
    return ranked

def get_all_resources(topic):
    return {
        "topic": topic,
        "links": get_links(topic),
        "articles": get_text(topic),
        "images": get_images(topic),
        "videos": get_videos(topic),
    }

resources = get_all_resources("Flutter")

# print(resources)

# print("\n*******ARTICLES*****\n")

# for article in resources["articles"]:
#     print(f"\n🔗 {article['title']} ({article['score']:.2f})")
#     print(f"URL: {article['link']}")
#     print(f"Summary: {article['summary']}")


# print("\n*****IMAGES*****\n")

# for img in resources['images']:
#     print(f"\nTitle: {img['title']}")
#     print(f"URL: {img['image']}")

# print("\n*****VIDEOS*****\n")

# for video in resources['videos']:
#     print(f"\nTitle: {video['title']}")
#     print(f"URL for Video: {video['href']}")
#     print(f"Desc: {video['body']}")
#     print(f"Upload Time: {video['upload_time']}")



# joblib.dump(model, 'model.pkl')

