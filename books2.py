from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: int | None = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Isuru",
                "description": "A new description of a book",
                "rating": 5
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "Isuru", "A very nice book!", 5),
    Book(2, "Be fast with FastAPI", "Isuru", "A great book!", 5),
    Book(3, "Master API", "Isuru", "A awesome book!", 5),
    Book(4, "HP1", "Author One", "Book Description", 2),
    Book(5, "HP2", "Author Two", "Book Description", 3),
    Book(6, "HP3", "Author Three", "Book Description", 1)
]


@app.get("/books")
async def get_all_books():
    return BOOKS

@app.get("/books/{book_id}")
async def read_book(book_id:int):
    for book in BOOKS:
        if book_id == book.id:
            return book
    return {"error":"Book not found"}

@app.get("/books/")
async def read_book_by_rating(book_rating:int):
    books_to_return:list[Book] = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.post("/create_book")
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    print(type(new_book))
    BOOKS.append(find_book_id(new_book))
    return BOOKS[-1]


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
