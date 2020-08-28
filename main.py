from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import config

driver = webdriver.Firefox(executable_path=r"C:\Users\Artur\Documents\Programmieren\geckodriver.exe")
driver.get("https://gym-old.eu/iserv/infodisplay/show/1")
sleep(1)

#todo Puts the page into full screen
# page = driver.find_element_by_name("_username")
# page.send_keys(Keys.F11)

#Finds and fills the username form
username_form = driver.find_element_by_name("_username")
username_form.clear()
username_form.send_keys(config.username)

#Finds and fills the password form
password_form = driver.find_element_by_name("_password")
password_form.clear()
password_form.send_keys(config.password)

#Clicks the login button
login_button = driver.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/form/div[3]/div[1]/button")
login_button.click()

#todo Screenshots the page (Screenshot too small to read)
driver.get_screenshot_as_file("screenshot.png")

