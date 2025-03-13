import re
from selenium.common.exceptions import NoSuchElementException
""" from image_uploader import add_to_queue, start_workers """
from selenium.webdriver.common.by import By
from config import region_map

def process_tab(driver, handle, url_list, save_to_database):
    # Sekme işlemleri
    driver.switch_to.window(handle)
    current_url = driver.current_url
    if current_url in url_list:
        return None

    # Sayfa verilerini saklamak için dictionary
    page_data = {"offerid": None}
    
    try:
        # Offer ID
        page_data["offerid"] = current_url.split("id=")[1]
    except IndexError:
        page_data["offerid"] = None

    # Game Name
    try:
        element = driver.find_element(By.XPATH, '//span[@class="inside"]')
        game = re.sub(r'Accounts', '', element.text).strip()
        if '(US)' in game:
            page_data.update({"platform": "US", "country": "United States", "game": game.replace('(US)', '').strip()})
        elif '(EU)' in game:
            page_data.update({"platform": "EU", "country": "Turkey", "game": game.replace('(EU)', '').strip()})
        else:
            page_data["game"] = game
    except NoSuchElementException:
        pass

    # Platform
    try:
        platform_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Platform"]/following-sibling::div[@class="text-bold"]')
        platform_text = platform_element.text
        platform_mapping = {
            "PS": "PlayStation", "PS4": "PlayStation 4", "PS5": "PlayStation 5",
            "Steam": "PC", "[Other]": "PC", "Social Club": "PC"
        }
        page_data["platform"] = platform_mapping.get(platform_text, platform_text)
    except NoSuchElementException:
        pass



    # Diğer Özellikler
    field_map = {
        "Server": "server", "Race": "race", "Faction": "faction",
        "Rank": "rank", "Level": "level", "Class": "class"
    }
    for field, key in field_map.items():
        try:
            element = driver.find_element(By.XPATH, f'//div[@class="param-item"]/h5[text()="{field}"]/following-sibling::div[@class="text-bold"]')
            page_data[key] = element.text.strip()
        except NoSuchElementException:
            pass

    # Başlık ve Açıklama
    try:
        title = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Short description"]/following-sibling::div').text
        page_data["title"] = re.sub(r'(Funpay|funpay)', "G2G", title)[:118]
    except NoSuchElementException:
        pass
    try:
        description = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Detailed description"]/following-sibling::div').text
        page_data["description"] = re.sub(r'(Funpay|funpay)', "Store", description)[:4990]
    except NoSuchElementException:
        pass

    # Fiyat
    try:
        price_element = driver.find_element(By.XPATH, '//span[@class="payment-value"]')
        price_match = re.search(r'(\d+(\.\d+)?)', price_element.text.strip())
        if price_match:
            page_data["price"] = float(price_match.group(1))
    except NoSuchElementException:
        page_data["price"] = None

    # Bölge (Region)
    try:
        region_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Server"]/following-sibling::div[@class="text-bold"]').text.strip()
        page_data["region"] = next((region_map[key] for key in region_map if key in region_element), region_element)
    except NoSuchElementException:
        pass

    # Veritabanı Kaydetme
    if page_data.get("offerid"):
        try:
            save_to_database([page_data])
        except Exception as e:
            print(f"Database save error: {e}")

    # Resim Kuyruğu Çalıştır
    start_workers(num_workers=5)
