from bs4 import BeautifulSoup
import requests
from prettytable import PrettyTable

table = PrettyTable()

dict_rating = {
      "one": '★ ⚝ ⚝ ⚝ ⚝',
      "two": '★ ★ ⚝ ⚝ ⚝', 
      "three": '★ ★ ★ ⚝ ⚝',
      "four": '★ ★ ★ ★ ⚝', 
      "five": '★ ★ ★ ★ ★'
    }

books_table = []

print("Enter the highest book price that you can accept (or 0 if you can accept them all)")
highest_price = float(input("> "))
print("Filtering...\n")
print("In what format do you want all the data to be displayed? (table/detail)")
format_info = input("> ").lower()
print("here you are...\n")

html_text = requests.get('https://books.toscrape.com/').text
soup = BeautifulSoup(html_text, 'lxml')
books = soup.find_all('li', class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
for book in books:
  price = book.find('p', class_="price_color").text.replace("Â", "")
  price_without_sign = price[1:]
  if highest_price >= float(price_without_sign) or highest_price == 0:
    book_tag = book.find('h3')
    book_name = book_tag.a["title"]
    more_info = book_tag.a["href"]
    rating = book.find('p').attrs['class'][1].lower()
    rating_to_stars = ''
    for rate in dict_rating:
      if rating == rate:
        rating_to_stars = dict_rating[rate]

    if format_info == "table":
      book_table = [book_name[:75], rating_to_stars, price]
      books_table.append(book_table)
    else:
      print(f"Book Name: {book_name}\nRating: {rating_to_stars}\nPrice: {price}\nMore Info: https://books.toscrape.com/{more_info}")
      print("")

if format_info == "table":
  table.field_names = ["Book Name", "Rating", "Price"]
  table.add_rows(books_table)
  print(table)