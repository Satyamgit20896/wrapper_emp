from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import mysql.connector
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

# 🔐 JWT Config
SECRET_KEY = "mysecretkey123"   # change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

security = HTTPBearer()

# Dummy login user (you can connect DB later)
USERNAME = "admin"
PASSWORD = "admin123"


# Employee Model
class Employee(BaseModel):
    id: int
    empName: str
    empDesignation: str
    empSalary: float


# Login Model
class LoginModel(BaseModel):
    username: str
    password: str


# MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="satyam_db"
    )


# 🔐 Token Create Function
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# 🔐 Verify Token Dependency
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid"
        )


# ✅ Login API → generate token
@app.post("/login")
def login(user: LoginModel):

    if user.username == USERNAME and user.password == PASSWORD:

        token = create_access_token(
            data={"sub": user.username}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": "5 minutes"
        }

    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


# ✅ Protected → Add employee
@app.post("/add_employee/")
def add_employee(emp: Employee, username: str = Depends(verify_token)):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO employee (id, empName, empDesignation, empSalary)
    VALUES (%s, %s, %s, %s)
    """

    values = (emp.id, emp.empName, emp.empDesignation, emp.empSalary)

    try:
        cursor.execute(query, values)
        conn.commit()

        return {
            "message": "Employee added successfully",
            "added_by": username
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ✅ Protected → Get all employees
@app.get("/employees/")
def get_all_employees(username: str = Depends(verify_token)):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM employee ORDER BY id DESC"

    try:
        cursor.execute(query)
        result = cursor.fetchall()

        return {
            "employees": result,
            "requested_by": username
        }

    finally:
        cursor.close()
        conn.close()


# ✅ Protected → Get employee by id
@app.get("/employee/{emp_id}")
def get_employee_by_id(emp_id: int, username: str = Depends(verify_token)):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM employee WHERE id = %s"

    cursor.execute(query, (emp_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result
    else:
        return {"message": "Employee not found"}