from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

import pandas as pd
import requests
import time


def get_initials(text):
    words = text.split()
    if len(words) == 1:
        return words[0][0].upper()
    elif len(words) > 1:
        return words[0][0].upper() + words[1][0].upper()
    return ""


def get_api_logs(email, password, response_codes=[400, 401, 429]):
    driver = webdriver.Chrome()
    driver.get("https://xbotic.cbots.live/admin/login")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
            print(f"Login successful for {email}")
        except TimeoutException:
            print(f"Login unsuccessful for {email}")
            driver.save_screenshot(f"login_failed_{email.replace('@','_at_')}.png")
            driver.quit()
            return []

        codes = []
        bot_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )

        for index in range(len(bot_cards)):
            try:
                cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
                )
                if index >= len(cards):
                    print(f"Bot card index {index} out of range, stopping loop.")
                    break

                card = cards[index]
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(card))
                card.click()
                time.sleep(2)  
                integrations_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "integrations-icon"))
                )
                integrations_button.click()

                # Click on API Logs 
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[3]//span[text()='API Logs']"))
                ).click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[title='Filter']"))).click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Response Code']"))).click()
                for code in response_codes:
                    try:
                        code_elem = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located(
                                (By.XPATH, f"//div[@class='css-1pcexqc-container']//div[text()='{code}']")
                            )
                        )
                        code_elem.click()
                    except TimeoutException:
                        
                        continue

                # Apply filter
                driver.find_element(By.XPATH, "//button[text()='Apply']").click()
                time.sleep(2)  

                #  (up to 100 entries)
                for i in range(100):
                    try:
                        path = f"/html/body/div[1]/div[1]/div/div[2]/div/div[3]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/ul[1]/li/div[2]/div[{i+1}]/div/div[1]/span"
                        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, path)))
                        span = driver.find_element(By.XPATH, path)
                        text = span.text.strip()
                        if text:
                            codes.append(text)
                    except TimeoutException:
                        break
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Bots']"))).click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                time.sleep(2) 

            except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                print(f"Error with bot card index {index}: {e}")
                try:
                    driver.find_element(By.XPATH, "//span[text()='Bots']").click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                except:
                    pass
                continue

        try:
            acc_text = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/div/div/section/div/div[2]/div[2]/div/div[1]/h1").text
            initials = get_initials(acc_text)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{initials}']")))
            driver.find_element(By.XPATH, f"//div[text()='{initials}']").click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Logout']")))
            driver.find_element(By.XPATH, "//span[text()='Logout']").click()
            print("Logout successful")
        except Exception:
            print("Logout skipped")

        driver.quit()

        allowed = set(str(c) for c in response_codes)
        filtered = list(set(c for c in codes if c in allowed))
        return filtered

    except Exception as e:
        print(f"Error during processing for {email}: {e}")
        driver.quit()
        return []


def get_logs_from_accounts(accounts):
    results = []

    for account in accounts:
        email = account.get("email")
        password = account.get("password")
        response_codes = account.get("response_codes", [400, 401, 429])

        if not email or not password:
            print(f"Skipping account with missing credentials.")
            results.append("")
            continue

        print(f"[*] Processing account: {email}")
        try:
            codes = get_api_logs(email, password, response_codes)
            results.append(", ".join(codes) if codes else "")
        except Exception as e:
            print(f"Error processing account {email}: {e}")
            results.append("")

    return results


sheet_url = "https://docs.google.com/spreadsheets/d/1Na8vuGZACh1XZPAV4rsppXvs2HOwfvxlKVmReE61bck/export?format=csv"
df = pd.read_csv(sheet_url).dropna(subset=["ID", "Password"])

accounts = [{
    "email": row["ID"],
    "password": row["Password"],
    "response_codes": [400, 401, 429]
} for _, row in df.iterrows()]

output_column = get_logs_from_accounts(accounts)

# Pad output if needed
output_column += [""] * (len(df) - len(output_column))

# Send results to your Google Apps Script endpoint
apps_script_url = "https://script.google.com/macros/s/AKfycbz7xh4JqUXKyO2VRk90-3LoupJiFWJtrY6rp9bzwIsJt4-IWQaNAYohaiDyrtXdySBE/exec"
payload = {
    "responses": output_column
}

print(payload)

try:
    res = requests.post(apps_script_url, json=payload)
    print("Status code:", res.status_code)
except Exception as e:
    print("Failed to send data:", e)
