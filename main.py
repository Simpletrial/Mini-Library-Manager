import json
from pathlib import Path
import requests

# ----------------- Book Class -----------------#
class Book:
    def __init__(self, title, author, year, genre):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre
        }

# ----------------- Library Manager -----------------#
class LibraryManager:
    def __init__(self, json_path="library.json"):
        self.json_path = Path(json_path)
        self.books = self.load_books()

    # Load books from JSON
    def load_books(self):
        if self.json_path.exists():
            with open(self.json_path, "r") as file:
                return json.load(file)
        return []

    # Save books to JSON
    def save_books(self):
        with open(self.json_path, "w") as file:
            json.dump(self.books, file, indent=4)

    # Add book to library
    def add_book(self, book):
        self.books.append(book.to_dict())
        self.save_books()
        print(f"✔ Book '{book.title}' added successfully.")

    # Search book in library
    def search_book(self, title):
        title = title.lower()
        results = [b for b in self.books if title in b["title"].lower()]

        if results:
            print("\n📚 Matching Books:")
            for b in results:
                print(f"- {b['title']} by {b['author']} ({b['year']}) - {b['genre']}")
        else:
            print("❌ No book found with that title.")

    # Fetch book from Google Books API
    def fetch_from_api(self, title):
        title = title.strip()

        # Ignore single letters
        if len(title) < 2:
            print("❌ No books found online.")
            return None

        print("\n🔎 Searching online…")
        url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
        response = requests.get(url)

        if response.status_code != 200:
            print("❌ Error fetching data from API.")
            return None

        data = response.json()
        if "items" not in data:
            print("❌ No books found online.")
            return None

        results = []

        for item in data["items"]:
            book_info = item["volumeInfo"]
            book_title = book_info.get("title", "")

            # Exact title match
            if book_title.lower() == title.lower():
                results = [book_info]
                break

            # Partial word match
            elif any(word.lower() == title.lower() for word in book_title.split()):
                results.append(book_info)

        # No matches found
        if not results:
            print("❌ No books found online.")
            return None

        # Return first matching book
        book_info = results[0]
        return {
            "title": book_info.get("title", "Unknown"),
            "author": ", ".join(book_info.get("authors", ["Unknown"])),
            "year": book_info.get("publishedDate", "Unknown")[:4],
            "genre": ", ".join(book_info.get("categories", ["Unknown"]))
        }


# ----------------- Menu Program -----------------#
def main():
    manager = LibraryManager()

    while True:
        print("\n====== MINI LIBRARY MANAGER ======")
        print("1. Add Book")
        print("2. Search Book")
        print("3. Fetch Book from API")
        print("4. Exit")

        choice = input("Enter option: ")

        if choice == "1":
            title = input("Title: ")
            author = input("Author: ")
            year = input("Year: ")
            genre = input("Genre: ")

            manager.add_book(Book(title, author, year, genre))

        elif choice == "2":
            title = input("Enter title to search: ")
            manager.search_book(title)

        elif choice == "3":
            title = input("Enter book title to search online: ")
            data = manager.fetch_from_api(title)

            if data:
                print("\n✔ Book found online:")
                print(data)

                save = input("Save this book? (y/n): ")

                if save.lower() == "y":
                    manager.add_book(Book(
                        data["title"],
                        data["author"],
                        data["year"],
                        data["genre"]
                    ))

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()
