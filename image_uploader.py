import requests
import json
import psycopg2
import logging
import time
from queue import Queue
from threading import Thread
import random
# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Information
IMGUR_CLIENT_ID = "1adabf60b0b0346"
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"
IMGBB_API_KEY = "69ae9dba48f255515fe7e64ad02bd58e"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Task queue
upload_queue = Queue()
proxies = [
    {"http": "http://kervan41:kervankervan@94.102.3.239:808", "https": "https://kervan41:kervankervan@94.102.3.239:808"},
    {"http": "http://kervan41:kervankervan@159.253.46.247:808", "https": "https://kervan41:kervankervan@159.253.46.247:808"},
    {"http": "http://kervan41:kervankervan@89.252.169.101:808", "https": "https://kervan41:kervankervan@89.252.169.101:808"},
    {"http": "http://kervan41:kervankervan@94.102.15.19:808", "https": "https://kervan41:kervankervan@94.102.15.19:808"},
    {"http": "http://kervan41:kervankervan@94.102.9.39:808", "https": "https://kervan41:kervankervan@94.102.9.39:808"},
    {"http": "http://kervan41:kervankervan@46.221.42.224:808", "https": "https://kervan41:kervankervan@46.221.42.224:808"},
    {"http": "http://kervan41:kervankervan@195.142.163.189:64200", "https": "https://kervan41:kervankervan@195.142.163.189:64200"},
    {"http": "http://kervan41:kervankervan@195.46.151.242:808", "https": "https://kervan41:kervankervan@195.46.151.242:808"},
    {"http": "http://kervan41:kervankervan@82.222.12.229:64200", "https": "https://kervan41:kervankervan@82.222.12.229:64200"},
    {"http": "http://kervan41:kervankervan@94.102.7.110:808", "https": "https://kervan41:kervankervan@94.102.7.110:808"}
]

def get_proxy():
    """Rastgele bir proxy seçer."""
    return random.choice(proxies)


def is_valid_image_url(url):
    """Filters URLs starting with specified domain."""
    return url.startswith("https://sfunpay.com/s/offer/")

def fetch_image_urls():
    """Fetches imgurls and offerids from the database."""
    with psycopg2.connect(dbname="postgres", user="postgres", password="159753Mert.", host="localhost", port="5432") as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT offerid, imgurl FROM scraped_data WHERE imgurl IS NOT NULL")
            image_data = cursor.fetchall()
    return {row[0]: [url for url in (json.loads(row[1]) if isinstance(row[1], str) else row[1]) if is_valid_image_url(url)] for row in image_data}

def retry_upload(func):
    """Decorator to retry upload in case of rate limiting."""
    def wrapper(image_url):
        for _ in range(5):  # Retry up to 5 times
            response = func(image_url)
            if response:
                return response
            time.sleep(10)  # Wait 10 seconds before retrying
        return None
    return wrapper

def upload_to_imgur(image_url):
    """Imgur üzerinde resim yükler."""
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    proxy = get_proxy()
    response = requests.post(IMGUR_UPLOAD_URL, headers=headers, data={"image": image_url}, proxies=proxy)
    if response.status_code == 200:
        logging.info(f"Uploaded to Imgur using proxy: {proxy['http']}")
        return response.json()["data"]["link"]
    logging.error(f"Imgur upload error: {response.status_code} - {response.text} using proxy: {proxy['http']}")
    return None

def upload_to_imgbb(image_url):
    """ImgBB üzerinde resim yükler."""
    proxy = get_proxy()
    response = requests.post(IMGBB_UPLOAD_URL, data={"key": IMGBB_API_KEY, "image": image_url}, proxies=proxy)
    if response.status_code == 200:
        logging.info(f"Uploaded to ImgBB using proxy: {proxy['http']}")
        return response.json()["data"]["url"]
    logging.error(f"ImgBB upload error: {response.status_code} - {response.text} using proxy: {proxy['http']}")
    return None

def upload_image(image_url):
    """Attempts to upload an image using both Imgur and ImgBB APIs."""
    imgur_url = upload_to_imgur(image_url)
    if not imgur_url:
        imgur_url = upload_to_imgbb(image_url)
    return imgur_url

def process_images_for_imgur():
    """Imgur için kuyruktan resim URL'leri alıp işler."""
    while not upload_queue.empty():
        offerid, image_urls = upload_queue.get()
        updated_urls = []
        for url in image_urls:
            new_url = upload_to_imgur(url)
            updated_urls.append(new_url if new_url else url)
        update_database(offerid, updated_urls)
        upload_queue.task_done()



def process_images_for_imgbb():
    """ImgBB için kuyruktan resim URL'leri alıp işler."""
    while not upload_queue.empty():
        offerid, image_urls = upload_queue.get()
        updated_urls = []
        for url in image_urls:
            new_url = upload_to_imgbb(url)
            updated_urls.append(new_url if new_url else url)
        update_database(offerid, updated_urls)
        upload_queue.task_done()


def update_database(offerid, updated_urls):
    """Updates the database with the new imgurls."""
    with psycopg2.connect(dbname="postgres", user="postgres", password="159753Mert.", host="localhost", port="5432") as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE scraped_data SET imgurl = %s WHERE offerid = %s", (json.dumps(updated_urls), offerid))
            conn.commit()

def start_processing(image_data):
    """İş parçacıklarını başlatır ve Queue'ya görevleri yerleştirir."""
    for offerid, urls in image_data.items():
        if urls:  # Sadece geçerli URL'ler için işlem yapılır
            upload_queue.put((offerid, urls))
        else:
            logging.info(f"Görsel bulunamadı veya geçersiz: {offerid}")
            
    threads = [
        Thread(target=process_images_for_imgur),
        Thread(target=process_images_for_imgbb)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

image_data = fetch_image_urls()
start_processing(image_data)