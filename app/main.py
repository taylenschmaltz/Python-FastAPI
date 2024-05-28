from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


try:
    conn = psycopg2.connect(host = 'localhost', database='fastapi', user='postgres', password='123', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("connection successful")
except Exception as error:
    print("failed to connect: " + error)

myPosts = [{"title": "og post", "content": "content", "id": 1}]



@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM fastapi""")
    posts = cursor.fetchall()
    print(posts)
    print("hi")
    return {"data": posts}



@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(newpost: Post):
    cursor.execute("""INSERT INTO fastapi (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (newpost.title, newpost.content, newpost.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post_id(id: int, response: Response):
    cursor.execute("""SELECT * FROM fastapi where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM fastapi where id = %s returning *""", (str(id)))
    deletedPost = cursor.fetchone()
    conn.commit()
    if deletedPost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE fastapi SET title = %s, content = %s, published = %s where id = %s returning *""", (post.title, post.content, post.published, str(id)))
    updatedPost = cursor.fetchone()
    conn.commit()
    if updatedPost == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {'data': updatedPost}