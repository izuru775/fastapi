from fastapi import FastAPI,Body
from pydantic import BaseModel,Field

app = FastAPI()

class Book:
    id:int
    title:str
    author:str
    description:str
    rating:int

    def __init__(self,id:int,title:str,author:str,description:str,rating:int):
        self.id =id
        self.title =title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel):
    id:int| None = None
    title:str =Field(min_length=3)
    author:str = Field(min_length=1)
    description:str = Field(min_length=1,max_length=100)
    rating:int = Field(gt=-1,lt=6)


BOOKS=[
    Book(1,"Computer Science Pro","Isuru","A very nice book!",5),
    Book(2,"Be fast with FastAPI","Isuru","A great book!",5),
    Book(3,"Master API","Isuru","A awesome book!",5),
    Book(4,"HP1","Author One","Book Description",2),
    Book(5,"HP2","Author Two","Book Description",3),
    Book(6, "HP3", "Author Three", "Book Description", 1)
]
@app.get("/books")
async def get_all_books():
    return BOOKS

@app.post("/create_book")
async def create_book(book:BookRequest):
    new_book =Book(**book.model_dump())
    print(type(new_book))
    BOOKS.append(find_book_id(new_book))
    return BOOKS[-1]


def find_book_id(book:Book):
    book.id = 1 if len(BOOKS)==0 else BOOKS[-1].id +1
    return book
