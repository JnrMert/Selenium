from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setup_driver import setup_driver
import time

def safe_click(driver, by, value):
    """ Güvenli tıklama işlemi için bir JavaScript yöntemi kullanır. """
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.5)  # Tıklamadan sonra sayfanın yüklenmesini bekleyin

def process_tabs(driver, start_page, end_page):
    """ 10'lu sekme açıp her sekmede işlem yapar ve sekmeleri kapatır. """
    # Sekmeleri aç
    for page_number in range(start_page, end_page - 1, -1):
        url = f"https://www.g2g.com/offers/list?cat_id=5830014a-b974-45c6-9672-b51e83112fb7&status=delisted_by_g2g&page={page_number}"
        driver.execute_script("window.open(arguments[0]);", url)
        time.sleep(1)  # Sekme açılmasını bekleyin

    # Açılan sekmelerde işlemleri yap
    for handle in reversed(driver.window_handles[1:]):
        driver.switch_to.window(handle)
        try:
            time.sleep(2)  # Sayfanın tam yüklenmesini bekleyin
            safe_click(driver, By.XPATH, '/html/body/div[1]/div/div[1]/main/div[3]/div[2]/div[2]/div/div[2]/table/thead/tr/th[1]/div/div/div')
            safe_click(driver, By.XPATH, '/html/body/div[1]/div/div[2]/footer/div/div[2]/button[1]/span[2]/span/i')
            safe_click(driver, By.XPATH, '/html/body/div[4]/div[2]/div/div/button[2]/span[2]/span')
            time.sleep(3)  # İşlemin tamamlanmasını bekleyin
        except Exception as e:
            print(f"Sekme işleminde hata oluştu: {e}")
        finally:
            # İşlem tamamlanan sekmeyi kapat
            driver.close()
            time.sleep(1)

    # Ana sekmeye dön
    driver.switch_to.window(driver.window_handles[0])

def main():
    driver = setup_driver()
    driver.get("https://www.g2g.com/offers/list?cat_id=5830014a-b974-45c6-9672-b51e83112fb7&status=delisted_by_g2g")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".q-pagination button .block")))
    last_page = min(76, max([int(el.text) for el in driver.find_elements(By.CSS_SELECTOR, ".q-pagination button .block") if el.text.isdigit()], default=0))

    if last_page == 0:
        raise ValueError("Son sayfa numarası bulunamadı")

    batch_size = 10
    for start_page in range(last_page, 0, -batch_size):
        end_page = max(1, start_page - batch_size + 1)
        print(f"Sayfalar işleniyor: {start_page} - {end_page}")
        process_tabs(driver, start_page, end_page)

    driver.quit()

if __name__ == "__main__":
    main()
