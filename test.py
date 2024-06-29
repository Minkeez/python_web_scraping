from bs4 import BeautifulSoup
import requests
from prettytable import PrettyTable
from urllib.parse import urljoin
from tqdm import tqdm
import logging
import argparse

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dict_rating = {
    "one": '★ ⚝ ⚝ ⚝ ⚝',
    "two": '★ ★ ⚝ ⚝ ⚝', 
    "three": '★ ★ ★ ⚝ ⚝',
    "four": '★ ★ ★ ★ ⚝', 
    "five": '★ ★ ★ ★ ★'
}

def get_user_input(prompt, default=None, cast_func=str):
    try:
        return cast_func(input(prompt) or default)
    except ValueError:
        logging.warning("Invalid input. Using default value.")
        return default

def get_book_info(book):
    try:
        price = book.find('p', class_="price_color").text.replace("Â", "").strip()
        price_without_sign = float(price[1:])
        book_tag = book.find('h3')
        book_name = book_tag.a["title"]
        more_info = book_tag.a["href"]
        rating = book.find('p').attrs['class'][1].lower()
        rating_to_stars = dict_rating.get(rating, '⚝ ⚝ ⚝ ⚝ ⚝')
        return book_name[:75], rating_to_stars, price, more_info, price_without_sign
    except AttributeError as e:
        logging.error(f"Error parsing book information: {e}")
        return None

def display_book_details(book_info):
    book_name, rating_to_stars, price, more_info, _ = book_info
    print(f"Book Name: {book_name}\nRating: {rating_to_stars}\nPrice: {price}\nMore Info: https://books.toscrape.com/{more_info}")
    print("")

def display_books_table(books_table):
    table = PrettyTable()
    table.field_names = ["Book Name", "Rating", "Price"]
    table.add_rows(books_table)
    print(table)

def get_categories():
    url = 'https://books.toscrape.com/index.html'
    try:
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'lxml')
        categories_sidebar = soup.find('div', class_="side_categories")
        parent_categories = categories_sidebar.find('li').ul
        categories = parent_categories.find_all('li')
        category_dict = {}
        for category in categories:
            category_name = category.find('a').text.strip()
            category_link = urljoin("https://books.toscrape.com", category.find('a')['href'])
            category_dict[category_name] = category_link
        return category_dict
    except requests.RequestException as e:
        logging.error(f"Error fetching categories: {e}")
        return {}

def scrape_books(selected_category, num_pages, highest_price, format_info):
    all_books_table = []
    all_book_details = []

    for start_page in tqdm(range(num_pages), desc="Scraping Pages"):
        if start_page == 0:
            url = selected_category
        else:
            url = selected_category.replace("index.html", f"page-{start_page+1}.html")
        logging.info(f"Fetching URL: {url}")
        try:
            html_text = requests.get(url).text
            soup = BeautifulSoup(html_text, 'lxml')
            books = soup.find_all('li', class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

            for book in books:
                book_info = get_book_info(book)
                if book_info:
                    _, _, _, _, price_without_sign = book_info
                    if highest_price >= price_without_sign or highest_price == 0:
                        if format_info == "table":
                            all_books_table.append(book_info[:3])
                        else:
                            all_book_details.append(book_info)
        except requests.RequestException as e:
            logging.error(f"Error fetching page: {e}")

    return all_books_table, all_book_details

def main():
    highest_price = get_user_input("Enter the highest book price that you can accept (or 0 if you can accept them all)\n> ", default=0, cast_func=float)
    format_info = get_user_input("In what format do you want all the data to be displayed? (table/detail)\n> ", default='table').lower()
    print("")

    categories = get_categories()
    print("Available categories:")
    for i, category in enumerate(categories.keys(), 1):
        print(f"{i}. {category}")
    print("")
    category_choice = get_user_input("Select a category by number (or press Enter for all categories):\n> ", default=0, cast_func=int)
    print("")

    if category_choice > 0 and category_choice <= len(categories):
        selected_category = list(categories.values())[category_choice - 1]
    else:
        selected_category = 'https://books.toscrape.com/catalogue/index.html'

    num_pages = get_user_input("How many pages do you want to scrape?\n> ", default=1, cast_func=int)
    print("")

    all_books_table, all_book_details = scrape_books(selected_category, num_pages, highest_price, format_info)

    print("Here you are...\n")
    if format_info == "table":
        display_books_table(all_books_table)
    else:
        for book_info in all_book_details:
            display_book_details(book_info)

if __name__ == "__main__":
    main()
