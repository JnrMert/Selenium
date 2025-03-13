# scraper.py

import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from config import url_list, unwanted_keywords, region_map, url_game_map
import re
from database import is_offerid_in_database, save_to_database, delete_old_offers  
import json
import math

page_data = {}
def scrape_urls(driver):
  data = []
  for url in url_list:
    driver.get(url)
    main_window = driver.current_window_handle
    game_name = url_game_map.get(url, "Unknown game")
    current_offerids = []
    while True:
        try:
            button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-default.margin-top.lazyload-more")
            time.sleep(0.4)
            if button.is_displayed():
                button.click()
            else:
                print("All Offers Shows.")
                break
        except NoSuchElementException:
            print("Buton bulunamadi.")
            break

    time.sleep(0.5)  # Bekleme s�resi (�rne�in, 2 saniye)


    
    elements = driver.find_elements(By.XPATH, '//a[contains(@class, "tc-item")]/div[@class="tc-user"]//span[@class="rating-mini-count"]')
    links = []
  
    for element in elements:
        price = None  # Reset price
        filtre_element = None  # Reset filter element
        filtre_text = ""  # Reset filter text
        media_user_info_element = ""
        if element.text.isdigit():                     ###########################################################################################################
            rating = int(element.text)
            parent_element = element.find_element(By.XPATH, './ancestor::a[contains(@class, "tc-item")]') if rating > 50 else None

            if parent_element is None:
                continue
            try:
                 media_user_info_element = parent_element.find_element(By.XPATH, './/div[@class="media-user-info"]')
                 if "years" not in media_user_info_element.text:
                      continue
            except NoSuchElementException:
                       continue
            try:
                price_element = parent_element.find_element(By.XPATH, './/div[@class="tc-price"]')
                price = float(price_element.text.replace('$', '').replace(',', '').strip())
            except NoSuchElementException:
                continue
            except ValueError:
                continue

            try:
                # Server değerini bulun
                filtre_element = parent_element.find_element(By.XPATH, './/div[@class="tc-server hidden-xs"]')
                filtre_text = filtre_element.text.strip()
            
                # "(EU)" veya "(US)" gibi metinleri kaldır ve boşlukları temizle
                cleaned_text = re.sub(r'\((EU|US)\)', '', filtre_text).strip()
            
                # Fazladan boşlukları kaldır
                page_data["server"] = re.sub(r'\s+', ' ', cleaned_text)
            
            except NoSuchElementException:
                pass
            # Filter based on text in class="tc-server hidden-xs"     YASAKLI KELIMELER!!!!!!!
            if any(keyword in filtre_text for keyword in unwanted_keywords):
                continue

            # FIYATTTTI BURDANNN AYARLAAAAAAA################################################################################
            if price is not None and price > 45:
                link = parent_element.get_attribute('href')
                links.append(link)
            try:
              title_element = parent_element.find_element(By.XPATH, './/div[@class="tc-desc-text"]')
              title_text = title_element.text
            # Rusça karakter içerip içermediğini kontrol et
              if re.search(r'[\u0400-\u04FF]', title_text):
                continue  # Rusça karakter içeriyorsa bu linki atla
            except NoSuchElementException:
              pass



    for link in links:
    # Yeni sekme a�ma
      try:
        offerid = link.split("id=")[1]
      except IndexError:
        print(f"Offerid bulunamadi: {link}")
        continue

    # Veritaban�nda kontrol et
      if is_offerid_in_database(offerid):
        print(f"Offerid zaten mevcut, sekme acilmadi: {offerid}")
        continue  # Bu linki atla
      driver.execute_script('window.open("{}");'.format(link))
      time.sleep(0.5)  

    for handle in driver.window_handles:
      driver.switch_to.window(handle)
      current_url = driver.current_url
      

      if current_url in url_list:
        continue
      
      try:
        element = driver.find_element(By.XPATH, '//span[@class="inside"]')
        game = element.text
        game = re.sub(r'Accounts', '', game).strip()
        if '(US)' in game:
            page_data["platform"] = "US"
            page_data["country"] = "United States"
            game = game.replace('(US)', '').strip()
        elif '(EU)' in game:
            page_data["platform"] = "EU"
            page_data["country"] = "Turkey"
            game = game.replace('(EU)', '').strip()
        page_data["game"] = game
      except NoSuchElementException:
          pass
      try:
        page_data["processed"] = False
        platform_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Platform"]/following-sibling::div[@class="text-bold"]')
        platform = platform_element.text
        if "PS" in platform:
           page_data["platform"] = "PlayStation"
        elif "PS4" in platform:
           page_data["platform"] = "PlayStation 4"
        elif "PS5" in platform:
           page_data["platform"] = "PlayStation 5"
        elif "Steam" in platform or "[Other]" in platform or "Social Club" in platform:
           page_data["platform"] = "PC"
        else:
           page_data["platform"] = platform
      except NoSuchElementException:
        pass
      try:
         offer_id = driver.current_url.split("id=")[1]
         page_data["offerid"] = offer_id
      except (IndexError, NoSuchElementException):
    # Handle the case where "id=" is not found or IndexError occurs
         page_data["offerid"] = None  # or any default value you prefer


      # Scrape Image URLs and upload to Imgur
      try:
          image_elements = driver.find_elements(By.XPATH, '//ul[@class="attachments-list"]/li/a')
    # imgurl için boş bir liste oluştur
          page_data["imgurl"] = []  
          for img_element in image_elements:
              image_url = img_element.get_attribute("href")
              page_data["imgurl"].append(image_url)  # Listeye her bir URL'yi ekle

    # Listeyi JSON formatına dönüştür
          page_data["imgurl"] = json.dumps(page_data["imgurl"])

      except NoSuchElementException:
          print("No images found for this offer.")
      try:
        server_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Server"]/following-sibling::div[@class="text-bold"]')
        server = server_element.text.strip() 
        if server == "Any":
            page_data["server"] = "EU"
        elif server == "(WG)":
            page_data["server"] = "EU"
        elif server == "America (Washington)":
            page_data["server"] = "Americas"
            
        elif server == "Europe (Amsterdam)":
            page_data["server"] = "Albion Europe"
            
        elif server == "Asia (Singapore)":
            page_data["server"] = "Albion Asia"
            
        else:
            page_data["server"] = server
      except NoSuchElementException:
        pass
                                                         ###GAME NAME

                                                           ##### REGION
      try:
        region_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Server"]/following-sibling::div[@class="text-bold"]').text
        region = region_element.strip()
        for key in region_map:
            if key in region:
                 page_data["region"] = region_map[key]
                 break
            else:
                 page_data["region"] = region
      except NoSuchElementException:
          pass
                                                                  #### RACE

      try:
        race_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Race"]/following-sibling::div[@class="text-bold"]')
        race = race_element.text
        page_data["race"] = race
      except NoSuchElementException:
        pass
                                                     #### GAME ama series i�in
      try:
        faction_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Faction"]/following-sibling::div[@class="text-bold"]')
        faction = faction_element.text
        match = re.search(r'Modern Warfare \d+', faction)
        if match:
           faction = match.group()
        page_data["faction"] = faction
      except NoSuchElementException:
        pass
                                             #### RANK

      try:
        rank_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Rank"]/following-sibling::div[@class="text-bold"]')
        rank = rank_element.text
        page_data["rank"] = rank[:4]
      except NoSuchElementException:
        pass

                                    #### LEVEL
      try:
        level_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Level"]/following-sibling::div[@class="text-bold"]')
        level = level_element.text
        level_numeric = int(level)
        level_rounded = round(level_numeric, -1)

        page_data["level"] = str(level_rounded)
      except NoSuchElementException:
        pass
                                  ####CLASS
      try:
        class_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Class"]/following-sibling::div[@class="text-bold"]')
        class_name = class_element.text
        page_data["class"] = class_name
      except NoSuchElementException:
        pass
                   ###Weapon Type
      """ try:
        wtype_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Weapon type"]/following-sibling::div[@class="text-bold"]')
        wtype_name = wtype_element.text
        page_data["weapon_type"] = wtype_name
      except NoSuchElementException:
        pass """
      """  try:
        prime_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="PRIME"]/following-sibling::div[@class="text-bold"]')
        prime = prime_element.text
        page_data["prime"] = prime
      except NoSuchElementException:
        pass """
      """ try:
        tower_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Town Hall Level"]/following-sibling::div[@class="text-bold"]')
        town_level = tower_element.text
        page_data["town_level"] = town_level
      except NoSuchElementException:
        pass """
      """ try:
        paragon_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Paragon level"]/following-sibling::div[@class="text-bold"]')
        p_level = paragon_element.text
        page_data["p_level"] = p_level
      except NoSuchElementException:
        pass """
      """ try:
        mmr_point_element = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="MMR"]/following-sibling::div[@class="text-bold"]')
        mmr_point = mmr_point_element.text
        page_data["mmr_point"] = mmr_point
      except NoSuchElementException:
        pass """
              ####Title
      try:
        title = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Short description"]/following-sibling::div').text
        if "Funpay" in title or "funpay" in title:
            title = title.replace("Funpay", "G2G").replace("funpay", "G2G").replace("https://", "link:").replace("https://youtu.be", "youtubelink:")
        page_data["title"] = title[:118]
      except NoSuchElementException:
        pass
              ####Description
      try:
        description = driver.find_element(By.XPATH, '//div[@class="param-item"]/h5[text()="Detailed description"]/following-sibling::div').text
        if "Funpay" in description or "funpay" in description:
            description = description.replace("Funpay", "Store").replace("funpay", "Store").replace("https://", "link:").replace("https://youtu.be", "youtubelink:")
        page_data["description"] = description[:4990]
      except NoSuchElementException:
        pass
              ######PRICE      
      try:
        price_element = driver.find_element(By.XPATH, '//span[@class="payment-value"]')
        price_text = price_element.text.strip()
    
        price_match = re.search(r'(\d+(\.\d+)?)', price_text)
    
        if price_match:
             price = float(price_match.group(1))
             page_data["price"] = price
        else:
             print("Gecerli bir fiyat formati bulunamadi!")
             page_data["price"] = None
      except NoSuchElementException:
         print("Fiyat elementi bulunamadi!")
         page_data["price"] = None

      data.append(page_data)

      if page_data.get("offerid"):
        try:
            save_to_database([page_data])  # Her bir ilan kayd�n� hemen veritaban�na g�nder
            print(f"Veri kaydedildi: {page_data.get('offerid')}")
        except Exception as e:
            print(f"Veri kaydedilemedi: {e}")
            
    for handle in driver.window_handles:
        if handle != main_window:  # Ana sekme de�ilse
           driver.switch_to.window(handle)  # O sekmeye ge�
           time.sleep(0.1)
           driver.close()  # Sekmeyi kapat
    try:
            delete_old_offers(game_name, current_offerids)
            print(f"Eski ilanlar silindi: {game_name}")
    except Exception as e:
            print(f"Eski ilanlar silinemedi: {e}")
            

    driver.switch_to.window(main_window)
    print(f"{url_game_map.get(url, 'Unknown game')} bitti.")
