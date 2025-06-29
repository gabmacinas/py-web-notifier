import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import webbrowser
import datetime
import subprocess
import os
from dotenv import load_dotenv
import signal
import sys
import json

time.sleep(15)

with open("endpoints.json") as f:
    endpoints = json.load(f)


load_dotenv()
CMD = """
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
"""


def handle_exit(signum, frame):
    print("\nExiting gracefully...")
    with open("output.log", "a") as myfile:
        myfile.write("Service Stopped\n")
    notify("Service Stopped", "Sonolus Scraping Stopped")
    sys.exit(0)


# Register signal handlers for SIGINT (Command + C) and SIGTERM
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


def notify(title, text):
    subprocess.call(["osascript", "-e", CMD, title, text])


notify("Service Started", "Sonolus Scraping Started")
with open("output.log", "a") as myfile:
    myfile.write("Service Started\n")
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    while True:
        for endpoint in endpoints["data"]:
            print(f"Checking {endpoint['name']} at {endpoint['url']}")
            url = endpoint["url"]
            retry_attempts = 3
            while retry_attempts > 0:
                try:
                    print(f"starting driver service")
                    driver = webdriver.Chrome(
                        service=webdriver.chrome.service.Service(
                            ChromeDriverManager().install()
                        ),
                        options=options,
                    )
                    print(f"Driver service started successfully")
                    print(
                        f"Attempting to access {endpoint['name']} {url} with {retry_attempts} retries left."
                    )
                    now = datetime.datetime.now()
                    driver.get(url)
                    content = driver.page_source
                    if "Start Testing" in content:
                        notify("Beta Available", f"This beta is available. {url}")
                        print(f"Beta Available!!! {url}")
                        start_testing_link = driver.find_element(
                            "xpath", '//a[text()="Start Testing"]'
                        ).get_attribute("href")
                        start_testing_link = start_testing_link.replace(
                            "https://", "itms-beta://"
                        )
                        print(start_testing_link)
                        with open("output.log", "a") as myfile:
                            myfile.write(
                                f"{now}: beta available. {start_testing_link}\n"
                            )
                        subprocess.call(
                            [
                                "osascript",
                                "-e",
                                f'tell application "Messages" to send "{endpoint["name"]} BOT: Beta is AVAILABLE!: {start_testing_link}" to buddy "{os.getenv("PHONE")}"',
                            ]
                        )
                        webbrowser.open(url)
                    else:
                        print(f"{now}: Beta is currently full {url}")
                        driver.quit()
                    break  # Exit retry loop if successful
                except Exception as e:
                    retry_attempts -= 1
                    print(
                        f"Error processing {url}. Retries left: {retry_attempts}. Error: {e}"
                    )
                    notify(
                        "Error",
                        f"Error processing {url}. Retries left: {retry_attempts}. ",
                    )
                    if retry_attempts == 0:
                        print(f"Failed to process {url} after 3 attempts.")
                        with open("output.log", "a") as error_file:
                            error_file.write(
                                f"{now}: Failed to process {url}. Error: {e}\n"
                            )
                    time.sleep(5)  # Wait before retrying
        time.sleep(10)
except Exception as e:
    print(f"An error occurred: {e}")
    handle_exit(None, None)
