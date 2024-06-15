from bs4 import BeautifulSoup
import re
import time
import urllib.request
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

def get_blog_data(keyword, include_words, exclude_words, start_date, end_date, display, client_id, client_secret):
    naver_urls, postdate, titles = [], [], []
    encText = urllib.parse.quote(keyword)
    
    start = 1
    while len(naver_urls) < display and start <= 1000:
        url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display=100&start={start}&sort=date"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))['items']
            for row in data:
                if 'blog.naver' in row['link']:
                    title = re.sub('<[^>]*>', '', row['title'])
                    if any(word in title for word in include_words) and not any(word in title for word in exclude_words):
                        naver_urls.append(row['link'])
                        postdate.append(row['postdate'])
                        titles.append(title)
                        print(f"URL: {row['link']}, Title: {title}, Postdate: {row['postdate']}")
            time.sleep(2)
        else:
            print(f"Error Code: {rescode}")
        start += 100
    return naver_urls[:display], postdate[:display], titles[:display]

def scrape_blog_content(urls, postdate):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--headless')
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(3)

    numbers, authors, contents, blogs_urls = [], [], [], []

    try:
        for idx, url in enumerate(urls):
            print(f"\n총 {len(urls)}건 중 {idx + 1}번째 블로그 데이터를 수집합니다=========")
            print(f"1. 블로그 주소: {url}")
            driver.get(url)
            time.sleep(5)
            try:
                iframe = driver.find_element(By.ID, "mainFrame")
                driver.switch_to.frame(iframe)
                source = driver.page_source
                html = BeautifulSoup(source, "html.parser")
                author_element = html.select_one("span.nick")
                content_element = html.select_one("div.se-main-container")
                author = author_element.get_text(strip=True) if author_element else "Unknown"
                content = content_element.get_text(strip=True) if content_element else "No content"
                numbers.append(idx + 1)
                authors.append(author)
                contents.append(content)
                blogs_urls.append(url)
                print(f"2. 작성자 닉네임: {author}")
                print(f"3. 작성일자: {postdate[idx]}")
                print(f"4. 블로그 내용: {content[:100]}...")  # 내용의 일부만 출력
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return numbers, authors, contents, blogs_urls

def save_data(numbers, authors, contents, postdate, blogs_urls, base_path):
    min_length = min(len(numbers), len(authors), len(contents), len(postdate), len(blogs_urls))
    df = pd.DataFrame({
        '블로그 주소': blogs_urls[:min_length],
        '작성자': authors[:min_length],
        '작성일자': postdate[:min_length],
        '내용': contents[:min_length]
    })

    os.makedirs(base_path, exist_ok=True)
    df.to_csv(os.path.join(base_path, 'blog.csv'), index=False)
    df.to_excel(os.path.join(base_path, 'blog.xlsx'), index=False)
    
    with open(os.path.join(base_path, 'blog.txt'), 'w', encoding='utf-8') as txt_file:
        for number, author, content, post_date, blog_url in zip(numbers, authors, contents, postdate, blogs_urls):
            txt_file.write(f"총 {len(numbers)}건 중 {number}번째 블로그 데이터를 수집합니다=========\n")
            txt_file.write(f"1. 블로그 주소: {blog_url}\n")
            txt_file.write(f"2. 작성자 닉네임: {author}\n")
            txt_file.write(f"3. 작성일자: {post_date}\n")
            txt_file.write(f"4. 블로그 내용: {content}\n\n")

def main():
    client_id = 'HV5ZQnbMfsPDuLzJiGre'
    client_secret = '4_QRebjQT6'
    
    keyword = input("1. 크롤링할 키워드는 무엇입니까?(예:여행): ")
    include_words = input("2. 결과에서 반드시 포함하는 단어를 입력하세요(예: 국내, 바닷가): ").split(', ')
    exclude_words = input("3. 결과에서 제외할 단어를 입력하세요(예:분양권, 해외)\n(여러개일 경우 , 로 구분해서 입력하고 없으면 엔터 입력하세요): ").split(', ')
    start_date = input("4. 조회 시작일자 입력 (예:2017-01-01): ").replace("-", "")
    end_date = input("5. 조회 종료일자 입력 (예:2017-12-31): ").replace("-", "")
    display = int(input("6. 크롤링 할 건수는 몇건입니까?(최대 1000건): "))
    base_path = input("7. 파일을 저장할 폴더명만 쓰세요(예:\\temp\\): ")

    naver_urls, postdate, titles = get_blog_data(keyword, include_words, exclude_words, start_date, end_date, display, client_id, client_secret)
    print(f"Found {len(naver_urls)} URLs")
    numbers, authors, contents, blogs_urls = scrape_blog_content(naver_urls, postdate)
    save_data(numbers, authors, contents, postdate, blogs_urls, base_path)

if __name__ == "__main__":
    main()
