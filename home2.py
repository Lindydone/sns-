import os
import requests

def download_images(keyword, num_images, download_folder, api_key):
    # Pixabay API URL 생성
    api_url = "https://pixabay.com/api/"
    params = {
        'key': api_key,
        'q': keyword,
        'image_type': 'photo',
        'per_page': num_images
    }

    # 폴더 생성
    os.makedirs(download_folder, exist_ok=True)

    # API 요청 및 응답 처리
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(f"Failed to retrieve images: {response.status_code}")
        return

    data = response.json()
    if 'hits' not in data:
        print("No images found.")
        return

    # 이미지 다운로드
    for i, hit in enumerate(data['hits'], start=1):
        img_url = hit['webformatURL']
        try:
            img_data = requests.get(img_url).content
            img_name = os.path.join(download_folder, f"{keyword}_{i}.jpg")
            with open(img_name, 'wb') as handler:
                handler.write(img_data)
            print(f"{i}/{num_images} {img_name} 다운로드 완료")
        except Exception as e:
            print(f"Failed to download image {img_url}: {e}")

def main():
    print("========================================")
    print("Pixabay API를 사용하여 이미지를 검색하여 수집하는 크롤러입니다")
    print("========================================")
    try:
        keyword = input("1. 크롤링할 이미지의 키워드는 무엇입니까?: ")
        num_images = int(input("2. 크롤링 할 건수는 몇건입니까?: "))
        download_folder = input("3. 파일이 저장될 경로만 쓰세요(예: c:\\temp\\): ")
        api_key = "44405880-44a3b44773e334236fa1f81f5"  # 입력하신 API 키

        download_images(keyword, num_images, download_folder, api_key)
    except ValueError:
        print("잘못된 입력입니다. 숫자를 입력해주세요.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
