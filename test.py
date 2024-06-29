from bs4 import BeautifulSoup
import requests
from prettytable import PrettyTable
from urllib.parse import urljoin

html_text = requests.get("https://books.toscrape.com/index.html").text
soup = BeautifulSoup(html_text, 'lxml')
categories_sidebar = soup.find('div', class_="side_categories")
parent_categories = categories_sidebar.find('li').ul
categories = parent_categories.find_all('li')
for category in categories:
  category_name = category.find('a').text.strip()
  category_link = category.find('a')['href']
  join_link = urljoin("https://books.toscrape.com", category_link)
  print(category_name)
  print(join_link)