from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pymongo import MongoClient
import certifi
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB Atlas Connection
uri = "mongodb+srv://satyamverma20896_db_user:z0BbR2MkfcbhOLmR@cluster0.st3j4ld.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tls=True, tlsCAFile=certifi.where())
db = client["react_db"]
collection = db["react_db"]

# JWT Config
SECRET_KEY = "mysecretkey"   # apna strong secret key rakho
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ✅ Login Request Body
class Login(BaseModel):
    username: str
    password: str


# ✅ Employee Model
class Employee(BaseModel):
    emp_id: int
    emp_name: str
    emp_designation: str
    emp_salary: int
    emp_experience: int
    emp_phone: str


# ✅ Token Generate Function
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


# ✅ Login API - Generate Token
@app.post("/login")
def login(user: Login):
    # Hardcoded credentials (demo purpose)
    if user.username == "react" and user.password == "admin123":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


# ✅ Token Verify Function
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ✅ Protected APIs
@app.post("/create")
def add_employee(employee: Employee, token: dict = Depends(verify_token)):
    employee_dict = employee.model_dump()
    result = collection.insert_one(employee_dict)
    employee_dict["_id"] = str(result.inserted_id)
    return {"message": "Employee added successfully", "data": employee_dict}


@app.get("/employees")
def get_all_employees(token: dict = Depends(verify_token)):
    employees = []
    for emp in collection.find():
        emp["_id"] = str(emp["_id"])
        employees.append(emp)
    return {"total_employees": len(employees), "data": employees}


@app.get("/employee/{emp_id}")
def get_employee(emp_id: int, token: dict = Depends(verify_token)):
    emp = collection.find_one({"emp_id": emp_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp["_id"] = str(emp["_id"])
    return {"data": emp}


@app.delete("/employee/{emp_id}")
def delete_employee(emp_id: int, token: dict = Depends(verify_token)):
    result = collection.delete_one({"emp_id": emp_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": f"Employee with emp_id {emp_id} deleted successfully"}
