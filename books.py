from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    category: str

app = FastAPI()

BOOKS = [
    Book(title= 'Title One', author ='Author One',category='science'),
    Book(title= 'Title Two', author ='Author Two',category='science'),
    Book(title= 'Title Three', author ='Author Three',category='history'),
    Book(title= 'Title Four', author ='Author Four',category='math'),
    Book(title= 'Title Five', author ='Author Five',category='math'),
    Book(title= 'Title Six', author ='Author Two',category='math')
]
@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/mybook")
async def read_all_book():
    return {"book title":"my favourite book"}

@app.get("/books/{book_title}")
async def read_book_title(book_title: str):
    for book in BOOKS:
        if str(book.title).casefold() == book_title.casefold():
            return book
    return {"error":"title not found"}

@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if str(book.category).casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/{book_author}/")
async def read_category_by_query(book_author: str,category:str):
    books_to_return = []
    for book in BOOKS:
        if str(book.author).casefold()==book_author.casefold():
            if str(book.category).casefold() == category.casefold():
                books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book:Book):
    print(new_book)
    BOOKS.append(new_book)
    return BOOKS[-1]

@app.put("/books/update_book")
async def update_book(book:Book):
    for i in range(len(BOOKS)):
        if BOOKS[i].title.casefold() == book.title.casefold():
            BOOKS[i] =book
            return BOOKS[i]
    return {"error":"title not found"}

@app.delete("/books/{book_title}")
async def delete_book(book_title: str):
    for book in BOOKS:
        if str(book.title).casefold() == book_title.casefold():
            BOOKS.remove(book)
            return book
    return {"error":"title not found"}

