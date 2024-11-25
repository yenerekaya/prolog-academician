import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json


warnings.filterwarnings("ignore", category=DeprecationWarning)


driver = webdriver.Chrome()


base_url = "https://fen.ege.edu.tr/tr-8623/akademik_kadromuz.html"
driver.get(base_url)

data = []  

try:
    time.sleep(5)  


    department_links = driver.find_elements(By.CSS_SELECTOR, "article p a")
    departments = [(link.text, link.get_attribute("href")) for link in department_links]

    print("Bölümler kontrol ediliyor...\n")
    for department_name, department_url in departments:
        print(f"Bölüm linkine gidiliyor: {department_url}")
        driver.get(department_url)
        time.sleep(3)  

        
        try:
            academician_links = driver.find_elements(By.CSS_SELECTOR, "td a[href^='https://unisis.ege.edu.tr/researcher']")
            academicians = [(link.text, link.get_attribute("href")) for link in academician_links]

            print(f"\n{department_name} için akademisyen linkleri kontrol ediliyor:")
            for academician_name, academician_url in academicians:
                print(f"Akademisyen linkine gidiliyor: {academician_url}")
                try:
                    driver.get(academician_url)
                    time.sleep(2)  

                    
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')

                    
                    researcher_name_div = soup.find("div", class_="col-12 fw-bold text-center fs-16")
                    researcher_name = researcher_name_div.text.strip() if researcher_name_div else None

                    
                    department_div = soup.find("div", text="Bölüm").find_next("div") if soup.find("div", text="Bölüm") else None
                    department = department_div.text.strip() if department_div else None

                    
                    discipline_div = soup.find("div", text="Ana bilim dalı").find_next("div") if soup.find("div", text="Ana bilim dalı") else None
                    discipline = discipline_div.text.strip() if discipline_div else None

                    
                    try:
                        publications_tab = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Yayınlar')]"))
                        )
                        publications_tab.click()

                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//p[@class='fs-14 text-wrap search-item-header']"))
                        )

                        
                        html_content = driver.page_source
                        soup = BeautifulSoup(html_content, 'html.parser')
                        publications = soup.find_all("p", class_="fs-14 text-wrap search-item-header")
                        publication_titles = [pub.text.strip() for pub in publications if pub.text.strip()]
                    except Exception:
                        publication_titles = []

                    
                    if not researcher_name and not department and not discipline and not publication_titles:
                        print(f"Bilgi alınamadı, sonraki akademisyene geçiliyor: {academician_url}")
                        continue

                    
                    data.append({
                        "name": researcher_name if researcher_name else "Bilgi bulunamadı",
                        "department": department if department else "Bilgi bulunamadı",
                        "discipline": discipline if discipline else "Bilgi bulunamadı",
                        "publications": publication_titles if publication_titles else [],
                        "profile_url": academician_url
                    })
                    print(f"Başarılı: {academician_name} - {academician_url}")

                except Exception as e:
                    print(f"Akademisyen bilgisi alınamadı: {academician_name} - {academician_url} - {e}")

        except Exception as e:
            print(f"{department_name} için akademisyen linkleri bulunamadı: {e}")

except Exception as e:
    print(f"Genel hata oluştu: {e}")

finally:
    driver.quit()


with open("academic_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Akademisyen verileri JSON dosyasına kaydedildi.")
