from fastapi import FastAPI
import uvicorn
from flask_cors import CORS

app = FastAPI()

@app.get("/")
def root():
    return {"message": "It works!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
CORS(app, origins=['http://localhost:3001'])

if __name__ == "__main__":
    print("=" * 50)
    print("Starting server...")
    print("Access at: http://127.0.0.1:5000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=5000)