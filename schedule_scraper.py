from bs4 import BeautifulSoup
import requests
import csv
# from main import login_and_get_source_code
import config
import base64


def print_html():
    html = login_and_get_source_code()
    print(html)
    print("Exit")


# print_html()
print(base64.b64encode(config.gmail_password.encode("utf-8")))

