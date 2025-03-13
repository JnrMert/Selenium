import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def input_text(driver, value, index):
    try:
        time.sleep(1)
        inputs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text']"))
        )
        if len(inputs) > index:
            inputs[index].send_keys(value)
        else:
            print(f"Belirtilen index ({index}) gecersiz. Sayfada yeterli sayida input elementi yok.")
    except NoSuchElementException:
        print("Input elementi bulunamadi.")
    except ElementNotInteractableException:
        pass  

def type_in_title_input(driver, input_text, value):
    
    try:
       input_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//input[@placeholder='{input_text}']"))
        )
       time.sleep(1)
       input_element.click
       time.sleep(1)
       input_element.send_keys(value)
   
    except NoSuchElementException:
             print("input_text HATA")
def type_in_textarea_input(driver, textarea_placeholder, value):
    try:
        textarea_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//textarea[@placeholder='{textarea_placeholder}']"))
        )
        time.sleep(1)
        textarea_element.click()
        time.sleep(0.10)
        textarea_element.send_keys(value)

    except NoSuchElementException:
        print(f"{textarea_placeholder} icin textarea bulunamadi.")



def click_combobox_and_type_value(driver, combobox_text, value):
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.CSS_SELECTOR, ".q-inner-loading"))
        )
        combobox = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(), '{combobox_text}')]"))
        )
        combobox.click()
        time.sleep(1)
        
    except NoSuchElementException:
        print("combobox_text HATA")
    except ElementNotInteractableException:
        pass  
    
    try:
        input_field = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@type='text']"))  
        )
        input_field.send_keys(value)
        time.sleep(2.5)
        
        # Değeri içeren (case-insensitive) ilk seçeneği bul
        matching_option = WebDriverWait(driver, 5).until(

EC.presence_of_all_elements_located((By.XPATH, f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), translate('{value}', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))]"))

)

        if matching_option:
             if value == 'Apex Legends' and len(matching_option) > 1:
              matching_option[1].click()
             else:
              matching_option[0].click()

        
    except NoSuchElementException:
        print("text HATA")
    except ElementNotInteractableException:
        pass  
               

def select_region(driver, combobox_text, region_value):
    
    try:
       combobox = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(), '{combobox_text}')]"))
       )
       combobox.click()
       region_option_xpath = f"//div[@class='q-item__section column q-item__section--main justify-center'][contains(text(), '{region_value}')]"
       region_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, region_option_xpath))
        )
       region_option.click()
    except Exception as e:
            #print(f"Region BULUNAMADI") 
            pass   

def send_value_to_input_by_label(driver, label_text, value):
    try:
        # "Stock" yazısını içeren span öğesini bul
        label_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(), '{label_text}')]/span"))
        )
        
        # Parent div'i bul
        parent_div = label_span.find_element(By.XPATH, "./ancestor::div[@class='col-md-4 col-12']")
        
        # Parent div'e göre kardeş (sibling) div'i bul
        sibling_div = parent_div.find_element(By.XPATH, "./following-sibling::div[@class='col-md-8 col-12']")
        
        # Sibling div içinde input elemanını bul
        input_element = sibling_div.find_element(By.XPATH, ".//input[@type='text']")
        
        # Input elemanına değer gönder
        input_element.click()
        input_element.clear()
        input_element.send_keys(value)
        

    except Exception:
        print(f"send_value_to_input_by_label hata oluştu: ")

def click_continue_button(driver, buton_text):
    
    continue_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, f"//span[@class='block' and contains(text(), '{buton_text}')]"))
    )
    continue_button.click()    
def click_radio_button(driver, radio_class, index):
     try:
        radio_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, radio_class))
        )
        radio_buttons[index].click()
     except NoSuchElementException:
        print(f"Radio butonu '{radio_class}' bulunamadi veya tiklanabilir degil.")
