
from setup_driver import setup_driver
from scraper import scrape_urls
from database import save_to_database, delete_old_offers

def main():
    # Selenium driver kurulumu
    driver = setup_driver()
    try:
        print("URL'leri kazımaya başlıyorum...")
        # URL'leri kazı
        scraped_data = scrape_urls(driver)

        # Kazınan her oyun için verileri işleme
        for game_name, game_data in scraped_data.items():
            # Veritabanına kaydet
            save_to_database(game_data)

            # Eski ilanları sil
            current_offerids = [item["offerid"] for item in game_data if "offerid" in item]
            delete_old_offers(game_name, current_offerids)
            print(f"{game_name} için veriler işlendi.")

    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
    finally:
        driver.quit()  # Driver'ı kapat

if __name__ == "__main__":
    main()
