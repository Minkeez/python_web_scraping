from bs4 import BeautifulSoup
import requests
from prettytable import PrettyTable
from urllib.parse import urljoin

def get_user_input(prompt, default=None, cast_func=str):
  try:
    return cast_func(input(prompt) or default)
  except:
    print("Invalid input. Using default value.")
    return default

def get_book_info(book):
  price = book.find('p', class_="price_color").text.replace("Â", "")
  price_without_sign = float(price[1:])
  book_tag = book.find('h3')
  book_name = book_tag.a["title"]
  more_info = book_tag.a["href"]
  rating = book.find('p').attrs['class'][1].lower()
  rating_to_stars = dict_rating.get(rating, '⚝ ⚝ ⚝ ⚝ ⚝')
  return book_name[:75], rating_to_stars, price, more_info, price_without_sign

def display_book_details(book_info):
  book_name, rating_to_stars, price, more_info, _ = book_info
  print(f"Book Name: {book_name}\nRating: {rating_to_stars}\nPrice: {price}\nMore Info: https://books.toscrape.com/{more_info}")
  print("")

def display_books_table(books_table):
  table = PrettyTable()
  table.field_names = ["Book Name", "Rating", "Price"]
  table.add_rows(books_table)
  print(table)

dict_rating = {
    "one": '★ ⚝ ⚝ ⚝ ⚝',
    "two": '★ ★ ⚝ ⚝ ⚝', 
    "three": '★ ★ ★ ⚝ ⚝',
    "four": '★ ★ ★ ★ ⚝', 
    "five": '★ ★ ★ ★ ★'
}

highest_price = get_user_input("Enter the highest book price that you can accept (or 0 if you can accept them all)\n> ", default=0, cast_func=float)
format_info = get_user_input("In what format do you want all the data to be displayed? (table/detail)\n> ", default='table').lower()
print("Here you are...\n")

html_text = requests.get('https://books.toscrape.com/').text
soup = BeautifulSoup(html_text, 'lxml')
books = soup.find_all('li', class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

books_table = []
for book in books:
  book_info = get_book_info(book)
  _, _, _, _, price_without_sign = book_info
  if highest_price >= price_without_sign or highest_price == 0:
    if format_info == "table":
      books_table.append(book_info[:3])
    else:
      display_book_details(book_info)
      
if format_info == "table":
  display_books_table(books_table)