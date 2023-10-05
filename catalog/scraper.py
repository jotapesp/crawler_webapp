from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, wait
from urllib.parse import urljoin, urlparse
import requests
import time
import numpy as np
import re
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import asyncio
import httpx

class Spider:

    def __init__(self, seed_url):
        self.seed_url = seed_url
        self.root_url = f'{urlparse(self.seed_url).scheme}://{urlparse(self.seed_url).netloc}'
        self.pool = ThreadPoolExecutor(max_workers=100)
        self.scraped_pages = set([])
        self.crawl_queue = Queue()
        self.crawl_queue.put(self.seed_url)
        self.pages = {'url': [],
                      'language': [],
                      'title': [],
                      'content': []}
        self.depth = 0
        self.branch = 0
        self.seeds = self.crawl_queue.qsize() - 1
        self.graph = {}
        self.scores = {}
        self.ranks = {}

    def get_urls(self, response, page_url):
        '''
        Extract URLs from page_url:
            - add them to the queue to be scraped if not scraped yet.
            - create the graphs at self.graph for PageRanks calculation later.
        Extract the page_url content (text) and keep it in a dict at self.pages
        for later TF-IDF use.
        '''

        if page_url not in self.pages['url']:
            bs = BeautifulSoup(response, 'html.parser')
            anchor_tags = bs.find_all('a', href=True)
            title_tag = bs.find("title")
            content = bs.find_all("p")
            title = ''
            lang = ''
            root = f'{urlparse(page_url).scheme}://{urlparse(page_url).netloc}'
            try:
                title = title_tag.text
            except Exception:
                print(f'Tag <title> não foi encontrada para página {page_url}')
            try:
                lang_tag = bs.html["lang"]
            except Exception:
                print(f'Tag <lang> não foi encontrada para página {page_url}')
            else:
                lang = lang_tag

            body_content = ' '.join([sentence.text for sentence in content])
            body_content = re.sub(r'\s+', ' ', body_content)
            body_content = body_content.strip()
            self.pages['url'].append(page_url)
            self.pages['language'].append(lang)
            self.pages['title'].append(title)
            self.pages['content'].append(body_content)

            for link in anchor_tags:
                url = link['href']

                if url.startswith('/') or url.startswith(root): #or not urlparse(url).netloc:
                    url = urljoin(root, url)

                if urlparse(url).fragment:
                    url = (urlparse(url).scheme + '://' + urlparse(url).netloc +
                           urlparse(url).path + urlparse(url).query)

                if page_url not in self.graph:
                    if (not url.startswith('#') and urlparse(url).netloc):
                        self.graph[page_url]= [f'{url}',]
                elif page_url in self.graph:
                    if (not url.startswith('#') and urlparse(url).netloc):
                        self.graph[page_url].append(f'{url}')

                no_scheme = (urlparse(url).netloc + urlparse(url).path + urlparse(url).query)
                if url not in self.scraped_pages and no_scheme not in self.scraped_pages:
                    if (not url.startswith('#') and urlparse(url).netloc):
                        self.crawl_queue.put(url)


    def tfidf_vectorize(self, tam=10):
        '''
        TF-IDF calculation using Sklearn library
        '''

        vectorizer = TfidfVectorizer()
        df = pd.DataFrame.from_dict(self.pages)
        indices = pd.Series(df.index, index=df['url']).drop_duplicates()
        pages = df['content']
        tfidf_matrix = vectorizer.fit_transform(pages)
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        idx = indices[self.seed_url]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        if tam != -1:
            sim_scores = sim_scores[1:tam + 1]
        else:
            sim_scores = sim_scores[1:]
        page_indices = [i for i, score in sim_scores]
        langs = ['pt', 'en', 'pt-br', 'pt-BR', '', 'en-us', 'en-US', 'en-UK', 'en-AU']
        return df[['title', 'url', 'content']].loc[df['language'].isin(langs)].iloc[page_indices].values.tolist()
        # if tam == -1:
        #     res = df[['title', 'url', 'content']].loc[df['language'].isin(langs)].values.tolist()
        # Total_Score = 2*(cosine-score * pagerank) / (cosine-score + pagerank)

    def post_scrape_callback(self, resp):
        result = resp.result()

        if result and result[0].status_code == 200:
            respon = result[0]
            url = result[1]
            self.get_urls(respon.text, url)


    def scrape_page(self, url):
        '''
        Make GET requests to the URLs in the queue
        Return the response and the URL that generated that response
        '''
        try:
            resp = requests.get(url, timeout=(3, 30))
            return [resp, url]
        except requests.RequestException:
            return


    def crawler(self):
        '''
        Crawler method.
        This method will get the URLs from the queue and asynchronously
        use scrape_page method
        '''
        inicio = time.time()
        while True:
            try:
                if self.depth > 5:
                    self.pool.shutdown()
                    break

                target_url = self.crawl_queue.get(timeout=60)

                if target_url not in self.scraped_pages:
                    self.scraped_pages.add(target_url)
                    future = self.pool.submit(self.scrape_page, target_url)
                    future.add_done_callback(self.post_scrape_callback)

                if self.branch < self.seeds:
                    self.branch += 1
                else:
                    self.branch = 0
                    self.seeds = self.crawl_queue.qsize() - 1
                    self.depth += 1

            except Empty:
                return
            except Exception as e:
                print(e)
                continue
        # self.pool.shutdown(wait=True)
        fim = time.time()
        print(f"tempo={fim-inicio} s")


    def get_ranks(self):
        '''
        method that will calculate PageRanks for the links extracted.
        '''
        print("Calculando PageRanks")
        d = 0.8
        numloops = 8
        npages = len(self.graph)
        for page in self.graph:
            self.ranks[page] = 1.0 / npages
        for i in range(numloops):
            new_ranks = {}
            for page in self.graph:
                new_rank = (1 - d) / npages
                for node in self.graph:
                    if page in self.graph[node]:
                        new_rank = new_rank + d * (self.ranks[node] / len(self.graph[node]))
                new_ranks[page] = new_rank
            self.ranks = new_ranks


    def sort(self, tam):
        '''
        This method returns a sorted list of tuples with the URLs and their
        respective PageRanks values ordered by PageRanks in descending order.
        'tam' defines how many results to be returned
        '''
        sorted_ranks = sorted(self.ranks.items(), key=lambda x: x[1], reverse=True)
        return sorted_ranks[:tam + 1]


class Crawler:

    def __init__(self, seed_url, client):
        self.seed_url = seed_url
        self.root_url = f'{urlparse(self.seed_url).scheme}://{urlparse(self.seed_url).netloc}'
        self.crawl_queue = asyncio.Queue()
        self.qsize = 0
        self.client = client
        self.graph = {}
        self.seeds = 0
        self.found_links = set()
        self.scraped = set()
        self.done = set()
        self.depth = 0
        self.branch = 0
        self.num_workers = 1000
        self.pages = {'url': [],
                      'language': [],
                      'title': [],
                      'content': []}
        self.ranks = {}
        self.start = time.time()

    async def run(self):
        await self.adding_found_links(set([self.seed_url]))
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
            ]

        await self.crawl_queue.join()
        for worker in workers:
            worker.cancel()

    async def worker(self):
        while True:
            try:
                await self.crawl()
            except asyncio.CancelledError:
                return

    async def crawl(self):
        url = await self.crawl_queue.get()
        self.qsize -= 1
        try:
            await self.scrape(url)
        except Exception as e:
            pass
        finally:
            self.crawl_queue.task_done()

    async def scrape(self, url):
        # await asyncio.sleep(.01) # connection limiter
        response = await self.client.get(url, follow_redirects=True)
        found_links = await self.get_data(response)
        await self.adding_found_links(found_links)
        if self.branch < self.seeds:
            self.branch += 1
        else:
            self.branch = 0
            self.seeds = self.qsize
            self.depth += 1
        self.done.add(url)

    async def get_data(self, response):
        page_url = str(response.url)
        response = response.text
        root = f'{urlparse(page_url).scheme}://{urlparse(page_url).netloc}'
        if page_url not in self.pages['url']:
            bs = BeautifulSoup(response, 'html.parser')
            anchor_tags = bs.find_all('a', href=True)
            title_tag = bs.find("title")
            content = bs.find_all("p")
            title = ''
            lang = ''

            try:
                title = title_tag.text
            except Exception:
                print(f'Tag <title> não foi encontrada para página {page_url}')
            try:
                lang_tag = bs.html["lang"]
            except Exception:
                print(f'Tag <lang> não foi encontrada para página {page_url}')
            else:
                lang = lang_tag

            body_content = ' '.join([sentence.text for sentence in content])
            body_content = re.sub(r'\s+', ' ', body_content)
            body_content = body_content.strip()
            self.pages['url'].append(page_url)
            self.pages['language'].append(lang)
            self.pages['title'].append(title)
            self.pages['content'].append(body_content)
            found = set()
            for link in anchor_tags:
                url = link['href']

                if url.startswith('/') or url.startswith(root): #or not urlparse(url).netloc:
                    url = urljoin(root, url)

                if urlparse(url).fragment:
                    url = (urlparse(url).scheme + '://' + urlparse(url).netloc +
                           urlparse(url).path + urlparse(url).query)

                if page_url not in self.graph:
                    if (not url.startswith('#') and urlparse(url).netloc):
                        self.graph[page_url]= [f'{url}',]
                elif page_url in self.graph:
                    if (not url.startswith('#') and urlparse(url).netloc):
                        self.graph[page_url].append(f'{url}')

                no_scheme = (urlparse(url).netloc + urlparse(url).path + urlparse(url).query)
                if (url not in self.scraped and url not in self.found_links and
                    no_scheme not in self.scraped and no_scheme not in self.found_links):
                    if (not url.startswith('#') and urlparse(url).netloc):
                        # and (urlparse(url).netloc != urlparse(page_url).netloc
                        # and urlparse(url).path != urlparse(page_url).path)
                        # and (urlparse(url).netloc != urlparse(self.seed_url).netloc
                        # and urlparse(url).path != urlparse(self.seed_url).path)):
                        # print(f"4-{url}")
                        found.add(url)
            self.found_links.update(found)
            return found

    async def adding_found_links(self, urls):
        new = urls - self.scraped
        self.scraped.update(new)

        for url in new:
            await self.grow_list(url)

    async def grow_list(self, url):
        if self.depth > 5:
            return
        self.qsize += 1
        await self.crawl_queue.put(url)

    def tfidf_vectorize(self, tam=10):
        '''
        TF-IDF calculation using Sklearn library
        '''
        try:
            vectorizer = TfidfVectorizer()
            df = pd.DataFrame.from_dict(self.pages)
            indices = pd.Series(df.index, index=df['url']).drop_duplicates()
            pages = df['content']
            tfidf_matrix = vectorizer.fit_transform(pages)
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
            idx = indices[self.seed_url]
            sim_scores = list(enumerate(cosine_sim[idx])) # 13, 35, 44, 31, 23
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            if tam != -1:
                sim_scores = sim_scores[1:tam + 1]
            else:
                sim_scores = sim_scores[1:]
            page_indices = [i[0] for i in sim_scores]
            langs = ['pt', 'en', 'pt-br', 'pt-BR', '', 'en-us', 'en-US', 'en-UK', 'en-AU']
            res = df[['title', 'url', 'content']].loc[df['language'].isin(langs)].iloc[page_indices].values.tolist()
        except ValueError:
            self.get_ranks()
            return self.sort(tam=tam)
        else:
            return res


    def get_ranks(self):
        '''
        method that will calculate PageRanks for the links extracted.
        '''
        print("Calculando PageRanks")
        d = 0.8
        numloops = 8
        npages = len(self.graph)
        for page in self.graph:
            self.ranks[page] = 1.0 / npages
        for i in range(numloops):
            new_ranks = {}
            for page in self.graph:
                new_rank = (1 - d) / npages
                for node in self.graph:
                    if page in self.graph[node]:
                        new_rank = new_rank + d * (self.ranks[node] / len(self.graph[node]))
                new_ranks[page] = new_rank
            self.ranks = new_ranks

    def sort(self, tam=-1):
        '''
        This method returns a sorted list of tuples with the URLs and their
        respective PageRanks values ordered by PageRanks in descending order.
        tam attribute defines how many results to be returned
        '''
        sorted_ranks = sorted(self.ranks.items(), key=lambda x: x[1], reverse=True)
        if tam == -1:
            return sorted_ranks
        return sorted_ranks[:tam + 1]


async def create_async_crawler(url):
    '''
    this function is the main function to return an instance of Crawler class and
    run the crawler.
    '''
    start = time.time()
    async with httpx.AsyncClient() as client:
        crawler = Crawler(url, client)
        await crawler.run()
        depth = crawler.depth
        # len_p = len(crawler.pages['url'])
        qsize = crawler.qsize
        found_l = len(crawler.found_links)
    end = time.time()
    print(f"tempo={end - start}")
    print(f"depth={depth}")
    print(f"qsize={qsize}")
    print(f"found links={found_l}")
    return crawler
