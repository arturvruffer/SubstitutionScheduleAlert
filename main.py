from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
from datetime import datetime


def get_and_send_substitution_schedule():
    login()
    get_screenshot()
    send_email()


# Logs into the IServ website to view the schedule
def login():
    global driver
    driver = webdriver.Firefox(executable_path=r"C:\Users\Artur\Documents\Programmieren\geckodriver.exe")
    driver.get("https://gym-old.eu/iserv/infodisplay/show/1")
    sleep(1)

    driver.maximize_window()

    # Finds and fills the username form
    username_form = driver.find_element_by_name("_username")
    username_form.clear()
    username_form.send_keys(config.iserv_username)

    # Finds and fills the password form
    password_form = driver.find_element_by_name("_password")
    password_form.clear()
    password_form.send_keys(config.iserv_password)

    # Clicks the login button
    login_button = driver.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/form/div[3]/div[1]/button")
    login_button.click()


# Saving the whole browser page as screenshot in directory
def get_screenshot():
    driver.get_screenshot_as_file("screenshot.png")
    driver.close()


# Send the screenshot as an attachment in an email using gmail
def send_email():
    # Getting and formatting the current date and time to print in the email
    today = datetime.now()
    date_string = today.strftime("%d.%m.%Y")
    time_string = today.strftime("%H:%M Uhr")
    # Defining variables used to send the email (Recipients, content etc.)
    sent_from = config.gmail_username
    send_to = config.mailing_list
    email_subject = "Vertretungsplan vom " + date_string
    email_message = "Im Anhang der heutige Vertretungsplan.\n(Stand: " + time_string + ")"
    file_location = "C:\\Users\\Artur\\Documents\\Programmieren\\SubstitutionScheduleAlert\\screenshot.png"

    # Constructing the email as MIME object
    msg = MIMEMultipart()
    msg["From"] = sent_from
    msg["To"] = ", ".join(send_to)
    msg["Subject"] = email_subject

    msg.attach(MIMEText (email_message, "plain"))

    # Attaching the screenshot to the email
    filename = os.path.basename(file_location)
    attachment = open(file_location, "rb")
    part = MIMEBase("application", "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment; filename= {}".format(filename))

    msg.attach(part)

    # Sending email. Using secure connection to login to the Gmail account.
    # IMPORTANT: Activate access by less secure apps in Gmail account
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo()
    server_ssl.login(config.gmail_username, config.gmail_password)
    email_text = msg.as_string()
    server_ssl.sendmail(sent_from, send_to, email_text)
    server_ssl.quit()

    print("Email successfully sent!")


get_and_send_substitution_schedule()

