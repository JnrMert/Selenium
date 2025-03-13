# -*- coding: utf-8 -*-
import time
import random
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from multiprocessing import Process
from selenium.webdriver.support import expected_conditions as EC  # EC'nin import edildiği satır
from g2g_utils import (input_text, type_in_title_input, type_in_textarea_input, 
                       click_combobox_and_type_value, click_continue_button, click_radio_button, 
                       select_region, send_value_to_input_by_label)
from database import Database



def round_level(level):
    try:
        level_int = int(level)
        if level_int < 20:
            return "30+"
        remainder = level_int % 10
        if remainder < 5:
            rounded_level = level_int - remainder
        else:
            rounded_level = level_int + (10 - remainder)
        return f"{rounded_level}+"
    except (ValueError, TypeError):
        return None    
    





def site_1_actions(browser_index):
    firefox_options = Options()
    firefox_options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
    firefox_options.add_argument('-profile')

    profiles = [
        'C:\\Users\\swag\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\0hqrip2p.def',
        'C:\\Users\\swag\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\y6ettm65.def2',
        'C:\\Users\\swag\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\zp8hjcuh.def3',
        'C:\\Users\\swag\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ygwxyry4.def4',
        'C:\\Users\\swag\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\aezyhznk.default-release'
    ]
    
    firefox_options.add_argument(profiles[browser_index])
    service = Service("./geckodriver.exe")
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.get("https://www.g2g.com/offers/sell?cat_id=5830014a-b974-45c6-9672-b51e83112fb7")
    
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "q-spinner-mat"))
        )
        print("Spinner kayboldu.")
    except TimeoutException:
        print("Spinner kaybolmadı veya bekleme süresi doldu.")
    
    db = Database()
    record = db.fetch_next_unprocessed_record()
    while record:
        try:
            offerid = record['offerid']
            game = record['game']
            platform = record['platform']
            country = record['country']
            server = record['server']
            region = record['region']
            race = record['race']
            faction = record['faction']
            rank = record['rank']
            level = record['level']
            class_name = record['class']
            title_name = record['title']
            description = record['description']
            price = record['price']
            imgurl = record['imgurl']
            
            if game == "Diablo 4":
                classes = {
                    "rogue": "Rogue",
                    "druid": "Druid",
                    "barbarian": "Barbarian",
                    "necromancer": "Necromancer",
                    "sorceress": "Sorceress"
                }
                class_name = classes.get(title_name.lower(), random.choice(list(classes.values())))
                platform = "Eternal - Softcore"
                record['platform'] = platform
            
            if game == "Escape from Tarkov":
                level = "20+"
                platforms = {
                    "Arena Breakout Infinite (PC)": "Edge of Darkness",
                    "eod": "Edge of Darkness",
                    "Edge": "Edge of Darkness",
                    "standart": "Standard",
                    "standard": "Standard",
                    "Prepare": "Prepare for Escape",
                    "left behind": "Left Behind"
                }
                platform = platforms.get(title_name.lower(), random.choice(list(platforms.values())))
                record['platform'] = platform
            
            if game == "Call of Duty":
                platform = "Others"
                platforms = {
                    "Warfare": "Modern Warfare 2",
                    "Black Ops": "Black Ops Cold War",
                    "Vanguard": "Vanguard",
                    "World War": "World War 2",
                    "Infinite": "Infinite Warfare",
                    "Warzone": "Warzone 2"
                }
                platform = platforms.get(title_name.lower(), random.choice(list(platforms.values())))
                record['platform'] = platform
                rank = "Bronze"
                ranks = {
                    "diamond": "",
                    "plat": "Platinum",
                    "gold": "Gold",
                    "silver": "Silver",
                    "crimson": "Crimson",
                    "Top": "Top 250",
                }
                rank = ranks.get(title_name.lower(), random.choice(list(ranks.values())))
                record['rank'] = rank
            
            game_mappings = {
                "World of Tanks": (game, platform, region, faction, "PC - EU"), 
                "Sea of Thieves": (game, "All Server", "All Server", faction, server),
                "PUBG": ("PlayerUnknown's Battlegrounds", "Steam", region, faction, server),
                "World of Warcraft Classic + Hardcore": ("WOW Classic Era / SoD / Hardcore", platform, region, faction, server),
                "World of Warcraft WotLK Classic": ("WOW WotLK Classic", platform, platform, faction, server),
                "Aion Classic": (game, platform, platform, faction, server),
                "Roblox": ("RBL", "Others", region, faction, server),
                "Tom Clancy's Rainbow Six": ("Tom Clancys Rainbow Six Siege", "PC" , region, faction, server),
                "Steam": ("Steam (Global)", platform, region, faction, server),
                "Summoners War: Sky Arena": ("Summoners War", "Europe", region, faction, server),
                "for Crossout": ("Crossout", "PC", region, faction, server),
                "World of Warcraft": ("World Of Warcraft", platform, platform, faction, server),
                "Apex Legends": (game, platform, region, faction, server),
                "Brawl Stars": ("BS", platform, region, faction, server),
                "for Fortnite": ("FN", platform, region, faction, server),
                "Elder Scrolls Online (ESO)": ("The Elder Scrolls Online (Global)", platform, region, faction, server),
                "Clash of Clans": ("Clash of Clans", platform, region, faction, server)
            }
            
            if game in game_mappings:
                game, platform, region, faction, server = game_mappings[game]
                record['game'] = game
                record['platform'] = platform
                record['region'] = region
                record['faction'] = faction
                record['server'] = server
            
            price = float(price)
            if 110 > price:
                new_price = int(round(float(price) * 1.7))
            else:
                new_price = int(round(float(price) * 1.5))
            
            game_combobox_data = {
                "RBL": [("Please select", "Others")],
                "AFK Arena": [("Please select", "IOS")],
                "League of Legends": [("Please select", region), ("Please select", "Smurf Accounts"),("Please select", "BE 50")],
                "Genshin Impact": [("Please select", "Europe"), ("Please select", "60"), ("Please select", "10+"),("Please select", "15+")],
                "World of Tanks": [("Please select", server)],           
                "Counter-Strike 2": [("Please select", "No Prime"), ("Please select", "Smurf Accounts"), ("Please select", "Rank Ready")],
                "Crossout": [("Please select", platform)],           
                "BS": [("Please select", "IOS")],          
                "EVE Online": [("Please select", "Tranquility")],               
                "Mobile Legends": [("Please select", "IOS")],
                "Albion Online": [("Please select", server)],
                "Honkai: Star Rail":[("Please select", region), ("Please select", "70"), ("Please select", "100+")],          
                "GTA 5 Online": [("Please select", "PC"),("Please select", "5000+"),("Please select", "500 Bil +")],
                "Clash Royale" : [("Please select", level), ("Please select", "Boot Camp"), ("Please select", "90+"),("Please select", "70+")],
                "Clash of Clans": [("Please select", "10"), ("Please select", "90+"), ("Please select", "70+"), ("Please select", "50+"), ("Please select", "20+")],
                "Escape from Tarkov": [("Please select", level), ("Please select", platform)],          
                "New World": [("Please select", server), ("Please select", "PC"),("Please select", "65") ],          
                "Apex Legends": [("Please select", rank), ("Please select", "400+"),("Please select", "50+"),("Please select", "10+")], 
                "Lost Ark": [("Please select", "Arcturus"), ("Please select", "50"), ("Please select", class_name)],          
                "Call of Duty": [("Please select", platform), ("Please select", "PC"), ("Please select", "Bronze"),("Please select", "30+")],
                "Diablo 4": [("Please select", "Season 7 - Softcore"), ("Please select", "100"), ("Please select", class_name)],
                "Raid: Shadow Legends": [("Please select", "IOS")],
                "Steam (Global)": [("Please select", "50+")],
                "World Of Warcraft": [("Please select", "Area 52"), ("Please select", class_name), ("Please select", "Blood Elf"),("Please select", "80"),("Please select", "Turkey")],
                "WOW WotLK Classic": [("Please select", "Gehennas"), ("Please select", class_name), ("Please select", "Blood Elf"),("Please select", "80"),("Please select", "Turkey")],
                "Aion Classic": [("Please select", faction), ("Please select", class_name), ("Please select", "50")],
                "Sea of Thieves": [("Please select", "All Server")],
                "Dota 2": [("Please select", "Rank Ready"), ("Please select", "1000+"), ("Please select", "5000+")],
                "Call of Duty Mobile": [("Please select", "IOS"), ("Please select", "Pro")],
                "Minecraft": [("Please select", "PC - Java"), ("Please select", "Hypixel"),("Please select", "UnRanked")],
                "FN": [("Please select", "Champion"), ("Please select", "1000+"),("Please select", "100+")],
                "Warframe": [("Please select", "PC"), ("Please select", "34")],
                "The Elder Scrolls Online": [("Please select", "EU - PC")],
                "PUBG Mobile": [("Please select", "PC")],
                "Star Citizen": [("Please select", "Main Server")], 
                "OverWatch 2": [("Please select", "Master"),("Please select", "50+"),("Please select", "300+")],
                "Path of Exile 2": [("Please select", "Early Access Standard"),("Please select", "PC"),("Please select", "10+"),("Please select", class_name)],
                "Path of Exile": [("Please select", "PC"),("Please select", "Level 71")],                  
                "Eve Echoes": [("Please select", "IOS")]
            }
            
            print("Verileri okudu. Isleniyor...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "q-spinner-mat"))
                )
                print("Spinner kayboldu.")
            except TimeoutException:
                print("Spinner kaybolmadı veya bekleme süresi doldu.")
            
            while True:
                try:
                    click_combobox_and_type_value(driver, "Select brand", game)
                    break  # Başarılı olursa döngüden çık
                except Exception as e:
                    print(f"Error in click_combobox_and_type_value: {e}")
                    time.sleep(1)  # Hata durumunda bekle ve tekrar dene
            
            time.sleep(0.5)
            
            try:
                select_region(driver, "Select region", region)
            except Exception as e:
                print(f"Error in select_region: {e}")
            
            time.sleep(0.5)
            
            try:
                click_continue_button(driver, "Continue")
            except Exception as e:
                print(f"Error in click_continue_button: {e}")
            
            time.sleep(0.5)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "q-spinner-mat"))
                )
                print("Spinner kayboldu.")
            except TimeoutException:
                print("Spinner kaybolmadı veya bekleme süresi doldu.")
            click_radio_button(driver, "q-radio__inner", 1)
            comboboxes_to_fill = game_combobox_data.get(game, [])
            for combobox_text, value in comboboxes_to_fill:
                try:
                    click_combobox_and_type_value(driver, combobox_text, value)
                except Exception as e:
                    print(f"Error in click_combobox_and_type_value for {combobox_text}: {e}")
            
            try:
                type_in_title_input(driver, "Offer title", f" {title_name}")
            except Exception as e:
                print(f"Error in type_in_title_input: {e}")
            
            try:
                type_in_textarea_input(driver, "Type offer description here", f"{offerid}\n{description}")
            except Exception as e:
                print(f"Error in type_in_textarea_input: {e}")
            

            
            
            
            if game == "Genshin Impact":
                try:
                    input_text(driver, "1", 0)
                except Exception as e:
                    print(f"Error in input_text for Genshin Impact: {e}")
            elif game == "Honkai: Star Rail":
                try:
                    input_text(driver, "1", 0)
                    input_text(driver, "1", 1)
                    input_text(driver, "1", 2)
                except Exception as e:
                    print(f"Error in input_text for Honkai: Star Rail: {e}")
            
            select_region(driver, "0 hour", "2 hour")
            
            
            
            type_in_title_input(driver, "To", "1")
            
            
            time.sleep(0.5)
            
            
            send_value_to_input_by_label(driver, "Default price (unit)", new_price)
            time.sleep(0.5)
            click_continue_button(driver, "Publish")
            
            
            time.sleep(5)
            driver.get("https://www.g2g.com/offers/sell?cat_id=5830014a-b974-45c6-9672-b51e83112fb7")
            
            try:
                db.cursor.execute("""
                    UPDATE scraped_data SET processed = TRUE WHERE offerid = %s;
                """, (offerid,))
                db.conn.commit()
                print("ILAN YAYINDA!")
            except Exception as e:
                print(f"Database error while updating processed status to TRUE: {e}")
            
            record = db.fetch_next_unprocessed_record()
        
        except Exception as e:
            print(f"OYUNDA HATA: . {e} HATA KODU...")
            driver.get("https://www.g2g.com/offers/sell?cat_id=5830014a-b974-45c6-9672-b51e83112fb7")
            try:
                db.cursor.execute("""
                    UPDATE scraped_data SET processed = FALSE WHERE offerid = %s;
                """, (offerid,))
                db.conn.commit()
                print(f"FALSE OLARAK DEĞİŞTİRDİM! : {offerid}")
            except Exception as db_error:
                print(f"Database error while updating processed status to FALSE: {db_error}")
            record = db.fetch_next_unprocessed_record()
    
    driver.quit()

if __name__ == "__main__":
    processes = []
    for browser_index in range(5):
        process = Process(target=site_1_actions, args=(browser_index,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
     
            
if __name__ == "__main__":
    thread1 = Process(target=site_1_actions)
    thread1.start()
    thread1.join()