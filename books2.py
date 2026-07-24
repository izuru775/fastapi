from fastapi import FastAPI,Body
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
async def create_book(book=Body()):
    BOOKS.append(book)
    return BOOKS[-1]