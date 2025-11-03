from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "It works!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("=" * 50)
    print("Starting server...")
    print("Access at: http://127.0.0.1:5000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=5000)