from fastapi import APIRouter, HTTPException, Depends, Header
from models.admin import AdminLogin, AdminRegister, AdminResponse, Token
from database.db import get_db
from utils.helpers import hash_password, verify_password, create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AdminResponse)
def register(admin: AdminRegister):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM admins WHERE username = ? OR email = ?", 
                   (admin.username, admin.email))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create admin
    hashed_pwd = hash_password(admin.password)
    cursor.execute(
        "INSERT INTO admins (username, email, password) VALUES (?, ?, ?)",
        (admin.username, admin.email, hashed_pwd)
    )
    conn.commit()
    
    admin_id = cursor.lastrowid
    cursor.execute("SELECT id, username, email FROM admins WHERE id = ?", (admin_id,))
    result = cursor.fetchone()
    conn.close()
    
    return AdminResponse(id=result[0], username=result[1], email=result[2])

@router.post("/login", response_model=Token)
def login(admin: AdminLogin):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM admins WHERE username = ?", (admin.username,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not verify_password(admin.password, result[3]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": admin.username, "id": result[0]})
    return Token(access_token=token, token_type="bearer")

def get_current_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload

@router.get("/me", response_model=AdminResponse)
def get_me(current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email FROM admins WHERE id = ?", 
                   (current_admin["id"],))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return AdminResponse(id=result[0], username=result[1], email=result[2])