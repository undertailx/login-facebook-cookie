# Key Components:
#
# 1. FacebookSeleniumSession class:
#    - __init__: Initializes the Chrome WebDriver with maximized window and sets a 10-second wait.
#    - manual_login: Opens Facebook (if not already open) and loops until the "c_user" cookie is detected,
#      indicating a successful login.
#    - save_cookies: After login, it retrieves cookies from the browser, filters them (retaining only important ones),
#      and writes them to a JSON file.
#    - load_cookies: Opens Facebook, reads cookies from the JSON file, adds them to the browser session, and refreshes
#      the page to apply them.
#    - close: Shuts down the WebDriver (closes the browser).
#
# 2. main() function:
#    - Checks if cookies.json exists.
#      • If not, it triggers manual login to let the user log in and then saves the cookies.
#      • If the file exists, it loads the cookies to attempt automatic login.
#    - Implements delays (using time.sleep) to ensure cookies are fully set/loaded before proceeding.
#    - Uses a try-finally block to ensure that the browser is always closed.
#
# End Key Components

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json
import time
import os.path

class FacebookSeleniumSession:
    def __init__(self):
    
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10) 

    def manual_login(self):
        try:
          
            if not self.driver.current_url.startswith('https://facebook.com'):
                self.driver.get("https://facebook.com")
           
            while True:
                try:
                    cookies = self.driver.get_cookies()
                    if any(cookie['name'] == 'c_user' for cookie in cookies):
                        print("Login successful!")
                        return True
                    time.sleep(1) 
                except:
                    continue
                    
        except Exception as e:
            print(f"Error checking login: {str(e)}")
            return False

    def save_cookies(self, cookie_file):
        cookies = self.driver.get_cookies()
        important_cookies = ['c_user', 'xs', 'fr', 'datr', 'sb']
        filtered_cookies = [
            {
                'domain': cookie['domain'],
                'name': cookie['name'],
                'value': cookie['value'],
                'path': cookie['path'],
                'secure': cookie['secure'],
                'httpOnly': cookie.get('httpOnly', False)
            }
            for cookie in cookies
            if cookie['name'] in important_cookies
        ]
        
        with open(cookie_file, 'w') as f:
            json.dump(filtered_cookies, f, indent=2)
        print(f"Cookies saved to file {cookie_file}")

    def load_cookies(self, cookie_file):
        try:
            self.driver.get("https://facebook.com")
            time.sleep(1)

            with open(cookie_file, 'r') as f:
                cookies = json.load(f)

            for cookie in cookies:
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', True)
                }
                self.driver.add_cookie(cookie_dict)

            self.driver.refresh()
            return True
        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    session = FacebookSeleniumSession()
    cookie_file = "cookies.json"
    
    try:
        if not os.path.exists(cookie_file):
            if session.manual_login():
                time.sleep(2)
                session.save_cookies(cookie_file)
                print("Cookies saved! Please run the program again")
                time.sleep(5)
                return
            else:
                print("Login unsuccessful!")
                return
        else:
            if session.load_cookies(cookie_file):
                print("Logged in with cookies successfully!")
                time.sleep(5)
            else:
                print("Login with cookies unsuccessful! Please delete cookies.json and try again")
                return
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
