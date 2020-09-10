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
from bs4 import BeautifulSoup
import csv


def get_and_send_substitution_schedule():
    source_code = login_and_get_source_code()

    # Saves html file of website
    file_path = r"C:\Users\Artur\Documents\Programmieren\SubstitutionScheduleAlert\html\\" + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".html"
    file_path_csv = r"C:\Users\Artur\Documents\Programmieren\SubstitutionScheduleAlert\csv\\" + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".csv"

    html_file = open(file_path, "w+")
    html_file.write(source_code)
    html_file.close()

    substitution_list = html_to_csv(file_path, file_path_csv)  # todo Pass "file_path" into function
    # get_screenshot()
    driver.close()
    # send_email()

    output_subs(substitution_list, "6a")
    output_subs(substitution_list, "7b")
    output_subs(substitution_list, "11")
    output_subs(substitution_list, "13")
    output_subs(substitution_list, "9")


# Logs into the IServ website to view the schedule
def login_and_get_source_code():
    global driver
    global html
    driver = webdriver.Firefox(executable_path=config.geckodriver_path)
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

    # Switch frame to iframe to access elements in substitution monitor
    iframe = driver.find_element_by_xpath("/html/body/div/div[2]/div[3]/div[2]/div/div/div/div/div[2]/div/div/div/iframe")
    driver.switch_to.frame(iframe)
    # Returns the source code of the page inside the iframe
    source_code = driver.page_source

    return source_code


# Saving the whole browser page as screenshot in directory
def get_screenshot():
    driver.get_screenshot_as_file("screenshot.png")


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


def html_to_csv(file_path, file_path_csv):  # todo Add "filename" as argument
    with open(file_path) as source_code:
        soup = BeautifulSoup(source_code, "lxml")

    # Find the relevant dividers corresponding to the two tables which are the schedule
    today_and_tomorrow = soup.find_all("div", class_="grupet_widget_ScrollableTable grupet_widget_AutoScrollingTable")

    # Create empty list containing both days
    substitution_list = \
        [
            [], []  # [today], [tomorrow] Each line in table of one day is a list of lines of table
        ]

    # Loops over the two separate tables of schedule and prints lines of table grouped together
    for num_of_day, day in enumerate(today_and_tomorrow):
        # print("DAY " + str(num_of_day+1) + "\n\n")
        num_of_lines = 0
        try:
            for num_of_cells, cell in enumerate(day.tbody.find_all("td"), start=1):
                if num_of_cells == 1 or num_of_cells % 8 == 0:
                    substitution_list[num_of_day].append([])

                if cell.text == "":
                    # print("NO CONTENT")
                    substitution_list[num_of_day][num_of_lines].append("No content")
                else:
                    # print(cell.text)
                    substitution_list[num_of_day][num_of_lines].append(cell.text)

                if num_of_cells != 1 and num_of_cells % 8 == 0:  # Formatting extracted contents for improved readability
                    # print("\n")
                    num_of_lines += 1

        except AttributeError:
            pass

    # todo Convert substitution list to csv file

    with open(file_path_csv, "w+", newline="") as csv_file:
        thewriter = csv.writer(csv_file)

        for num_of_day, day in enumerate(substitution_list):
            for num_of_line, line in enumerate(day):
                thewriter.writerow(line)

    return substitution_list


def output_subs(substitution_list, school_class):
    no_substitutions = True
    output_substitution_list = []
    for num_of_day, day in enumerate(substitution_list):
        for num_of_line, line in enumerate(day):
            try:
                if school_class in line[2]:
                    output_substitution_list.append(line)
                    no_substitutions = False
            except:
                pass

    if no_substitutions:
        print("Keine Vertretung für die", school_class)
    else:
        print("Vertretungen für die {}:".format(school_class))
        for substitution in output_substitution_list:
            print(substitution)
    print("")


get_and_send_substitution_schedule()
