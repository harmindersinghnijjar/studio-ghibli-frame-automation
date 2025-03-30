import os
import time
import logging
import getpass
import pygetwindow as pywin
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

FRAME_DIR = "E:\\YouTube\\StudioGhibli\\sparse_frames"
IMAGE_EXTENSION = ".jpg"


def setup_logger():
    logger = logging.getLogger("GhibliAutomation")
    logger.setLevel(logging.INFO)

    if not os.path.exists("logs"):
        os.makedirs("logs")

    file_handler = logging.FileHandler(f"logs/{time.strftime('%Y-%m-%d')}.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = setup_logger()


class StudioGhibliLoader:
    def __init__(self, driver, upload_folder):
        self.driver = driver
        self.upload_folder = upload_folder
        self.page_opened = False

    def open_page(self):
        if not self.page_opened:
            self.driver.get("https://chatgpt.com/")
            logger.info("Navigating to ChatGPT...")
            time.sleep(15)
            self.page_opened = True

    def click_add_file(self):
        logger.info("Clicking add file button...")
        element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Upload files and more"]')
            )
        )
        self._highlight_element(element)
        element.click()
        logger.info("Clicked add file button.")
        time.sleep(5)
        self.click_upload_from_device()

    def click_upload_from_device(self):
        logger.info("Clicking 'Upload from device'...")
        element = self.driver.find_element(
            By.XPATH, "//div[normalize-space()='Upload from computer']"
        )
        self._highlight_element(element)
        element.click()
        logger.info("Clicked 'Upload from device'.")
        time.sleep(5)

    def upload_file(self, file_name):
        logger.info(f"Uploading file: {file_name}")
        full_path = os.path.abspath(os.path.join(self.upload_folder, file_name))
        file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
        file_input.send_keys(full_path)
        time.sleep(15)

        open_window = pywin.getWindowsWithTitle("Open")
        if open_window:
            open_window[0].close()
            logger.info("Closed the Open window.")
        else:
            logger.info("No Open window found.")

        time.sleep(15)
        logger.info(f"Uploaded: {full_path}")

    def enter_prompt(self, prompt_text):
        element = self.driver.find_element(
            By.CSS_SELECTOR,
            "div[class*='text-token-text-primary'][class*='default-browser']",
        )
        self._highlight_element(element)
        try:
            element.click()
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            raise

        pyautogui.click(element.location["x"] + 10, element.location["y"] + 10)
        time.sleep(2)
        pyautogui.typewrite(prompt_text)
        logger.info("Entered prompt.")
        time.sleep(5)

    def submit_remix(self):
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "div[class='ml-auto flex items-center gap-1.5']"
        )
        self._highlight_element(submit_button)
        submit_button.click()
        logger.info("Clicked submit button.")
        time.sleep(30)

    def download_image(self, index):
        xpath = f"(//button[@aria-label='Download this image'])[{index}]"
        logger.info("Waiting indefinitely for download button to appear...")

        download_button = None
        while download_button is None or not download_button.is_displayed():
            try:
                download_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if not download_button.is_displayed():
                    logger.info("Button found but not visible, retrying...")
                    time.sleep(5)
            except Exception:
                logger.info("Still waiting for download button...")
                time.sleep(5)

        WebDriverWait(self.driver, 0).until(
            lambda d: download_button.is_enabled() and download_button.is_displayed()
        )

        self._highlight_element(download_button)
        download_button.click()
        logger.info("Clicked download button.")
        time.sleep(15)

    def run_all(self, file_name, prompt_text, image_index):
        self.open_page()
        self.click_add_file()
        self.upload_file(file_name)
        self.enter_prompt(prompt_text)
        self.submit_remix()
        self.download_image(image_index)
        logger.info("Completed all steps.")

    def _highlight_element(self, element):
        self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
        time.sleep(5)
        self.driver.execute_script("arguments[0].style.border=''", element)


def main():
    os.system("taskkill /im chrome.exe /f")
    logger.info("Starting Ghibli Image Automation...")

    options = uc.ChromeOptions()
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    options.add_argument(
        f"--user-data-dir=C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data"
    )

    driver = uc.Chrome(
        executable_path=chrome_path,
        options=options,
        headless=False,
        use_subprocess=True,
    )

    uploader = StudioGhibliLoader(driver, FRAME_DIR)

    try:
        images = sorted(
            [f for f in os.listdir(FRAME_DIR) if f.endswith(IMAGE_EXTENSION)]
        )
        for index, image_file in enumerate(images, start=1):
            logger.info(f"Processing image {index}/{len(images)}: {image_file}")
            ghibli_prompt = "studio ghibli style"
            uploader.run_all(image_file, ghibli_prompt, index)
            logger.info(f"Completed processing {image_file}.")
            time.sleep(10)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        time.sleep(5)
        driver.quit()
        logger.info("Driver closed.")


if __name__ == "__main__":
    main()
