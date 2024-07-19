#Credits: Christopher Gallinger-Long
import os
import App
import time
import pygame
import keyboard
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def get_login():
    login_info = App.login_info

    return login_info


def play_sound():
    pygame.mixer.init()
    # Construct the absolute path
    file_path = os.path.abspath(os.path.join('sound', 'Ping.wav'))

    # Check if the file exists before trying to play it
    if os.path.isfile(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # wait for music to finish playing
            pygame.time.Clock().tick(10)
    else:
        print(f"File {file_path} not found")

def login_and_verify(driver, login):
    driver.get('https://service.uoregon.edu/TDNext/Home/Desktop/Desktop.aspx')

    try:
        # Detect username field by HTML ID and enter login info
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        username_field.send_keys(login[0])

        # Detect password field by HTML ID and enter login info
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        password_field.send_keys(login[1])

        # Detect login button and press it
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="submit"]'))
        )
        login_button.click()

        # Wait for the page to load and DUO verification to be completed
        verification_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'verification-code'))
        )
        verification_code_element = driver.find_element(By.CLASS_NAME, 'verification-code')
        verification_code = verification_code_element.text

        print(f'DUO Verification Code: {verification_code}')

        try:
            # Wait for the specific element in the content you want to scrape
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'trust-browser-button'))
            )
            yes_device_button = driver.find_element(By.ID, 'trust-browser-button')
            yes_device_button.click()
        except TimeoutException:
            print("Device check not found, proceeding without it.")

    except Exception as e:
        print(f"An error occurred during login: {e}")


def check_for_ticket(driver):
    try:
        # Check if content is within an iframe switch if true
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            driver.switch_to.frame(iframes[0])

        time.sleep(5)

        try:
            # Wait for the specific element in the content you want to scrape
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//td[text()="New"]'))
            )
            print("New ticket found!")
            play_sound()
        except TimeoutException:
            print("No new ticket found.")

    except NoSuchElementException as e:
        print(f"The table element was not found: {e}")
    except TimeoutException as e:
        print(f"Timed out waiting for element: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure we switch back to the default content
        driver.switch_to.default_content()

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    while not App.login_info:
        time.sleep(1)
    login = get_login()

    try:
        login_and_verify(driver, login)
        print("Press ESC to exit")
        while True:
            if keyboard.is_pressed('esc'):
                print("ESC key pressed. Stopping the ticket checker.")
                break
            check_for_ticket(driver)
            time.sleep(10)  # Wait for 10 second before checking again
    except KeyboardInterrupt:
        print("Stopping the ticket checker.")
    finally:
        driver.quit()



if __name__ == '__main__':
    # Start the Flask app in a separate thread
    flask_thread = Thread(target=App.run_flask)
    flask_thread.start()

    # Give Flask a moment to start up
    time.sleep(1)
    # Open the web browser
    App.open_browser()

    # Run the main function
    main()