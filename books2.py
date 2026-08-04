from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date:int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int,published_date:int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: int | None = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date:int =Field(gt=1999,lt=2040)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Isuru",
                "description": "A new description of a book",
                "rating": 5,
                "published_date":2024
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "Isuru", "A very nice book!", 5,2023),
    Book(2, "Be fast with FastAPI", "Isuru", "A great book!", 5,2025),
    Book(3, "Master API", "Isuru", "A awesome book!", 5,2014),
    Book(4, "HP1", "Author One", "Book Description", 2,2025),
    Book(5, "HP2", "Author Two", "Book Description", 3,2018),
    Book(6, "HP3", "Author Three", "Book Description", 1,2021)
]


@app.get("/books",status_code=status.HTTP_200_OK)
async def get_all_books():
    return BOOKS

@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def read_book(book_id:int=Path(gt=0)):
    for book in BOOKS:
        if book_id == book.id:
            return book
    raise HTTPException(status_code=404,detail="Item not found")

@app.get("/books/",status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating:int= Query(gt=0,lt=6)):
    books_to_return:list[Book] = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/",status_code=status.HTTP_200_OK)
async def read_book_by_published_date(published_date:int=Query(gt=1991,lt=2040)):
    books_to_return =[]
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create_book",status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    print(type(new_book))
    BOOKS.append(find_book_id(new_book))

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book:BookRequest):
    book_updated =False
    new_book:Book = Book(**book.model_dump())
    for i in range(len(BOOKS)):
        if BOOKS[i].id == new_book.id:
            BOOKS[i] = new_book
            book_updated = True
    if not book_updated:
        raise HTTPException(status_code=404,detail="Book not found")


@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int=Path(gt=0)):
    book_deleted =False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break
    if not book_deleted:
        raise HTTPException(status_code=404,detail="Book not found")



def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
