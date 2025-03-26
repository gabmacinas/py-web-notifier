import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import webbrowser
import datetime;
import subprocess;
import os;
from dotenv import load_dotenv
load_dotenv()
import signal
import sys

CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''

def handle_exit(signum, frame):
    print("\nExiting gracefully...")
    with open("log.txt", "a") as myfile:
        myfile.write("Service Stopped\n")
    notify("Service Stopped", "Sonolus Scraping Stopped")
    sys.exit(0)

# Register signal handlers for SIGINT (Command + C) and SIGTERM
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def notify(title, text):
  subprocess.call(['osascript', '-e', CMD, title, text])

notify("Service Started", "Sonolus Scraping Started")
with open("log.txt", "a") as myfile:
    myfile.write("Service Started\n")
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

urls = os.getenv('URLS').split(",")

try:
    while True:
        for url in urls:
            driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)
            now = datetime.datetime.now()
            driver.get(url)
            content = driver.page_source
            if "Start Testing" in content:
                notify("Beta Available", f"This beta is available. {url}")
                print(f"Beta Available!!! {url}")
                start_testing_link = driver.find_element("xpath", '//a[text()="Start Testing"]').get_attribute("href")
                start_testing_link = start_testing_link.replace("https://", "itms-beta://")
                print(start_testing_link)
                with open("success.txt", "a") as myfile:
                    myfile.write(f"{now}: beta available. {start_testing_link}\n")
                subprocess.call(['osascript', '-e', f'tell application "Messages" to send "SONOLUS BOT: Beta is AVAILABLE!: {start_testing_link}" to buddy "{os.getenv("PHONE")}"'])
                webbrowser.open(url)
            else:
                print(f"{now}: Beta is currently full {url}")            
                driver.quit()
        time.sleep(10)
except Exception as e:
    print(f"An error occurred: {e}")
    handle_exit(None, None)

