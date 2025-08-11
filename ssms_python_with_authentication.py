from flask import Flask, jsonify, request, Response
import pyodbc
import base64

app = Flask(__name__)

# 🔐 Basic Auth credentials
USERNAME = 'satyam'
PASSWORD = 'Pass@word1'

# 🔐 Auth check decorator
def require_auth(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

        encoded_credentials = auth.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        user, pwd = decoded_credentials.split(':')

        if user != USERNAME or pwd != PASSWORD:
            return Response('Invalid credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 🔗 Database connection details
server = r'DESKTOP-G1HG1TH\SQLEXPRESS'
database = 'Excel_Data'
driver = '{SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# 🔌 Connect to SQL Server
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("✅ Connected to SQL Server.")
except Exception as e:
    print("❌ Connection failed:", e)
    exit()

# 📡 GET all employees
@app.route('/employees', methods=['GET'])
@require_auth
def get_employees():
    try:
        cursor.execute("SELECT * FROM [dbo].[OLE DB Destination]")
        rows = cursor.fetchall()

        employees = []
        for row in rows:
            employee = {
                'Employee ID': row[0],
                'Full Name': row[1],
                'Gender': row[2],
                'Age': row[3],
                'Department': row[4],
                'Designation': row[5],
                'Joining Date': str(row[6]),
                'Location': row[7],
                'Experience (Years)': row[8],
                'Monthly Salary (₹)': float(row[9]),
                'Performance Rating': row[10],
                'Work Mode': row[11]
            }
            employees.append(employee)

        return jsonify(employees)

    except Exception as e:
        return jsonify({'error': str(e)})

# 📡 GET employee by string ID
@app.route('/employees/<emp_id>', methods=['GET'])
@require_auth
def get_employee_by_id(emp_id):
    try:
        query = "SELECT * FROM [dbo].[OLE DB Destination] WHERE [Employee ID] = ?"
        cursor.execute(query, emp_id)
        row = cursor.fetchone()

        if row:
            employee = {
                'Employee ID': row[0],
                'Full Name': row[1],
                'Gender': row[2],
                'Age': row[3],
                'Department': row[4],
                'Designation': row[5],
                'Joining Date': str(row[6]),
                'Location': row[7],
                'Experience (Years)': row[8],
                'Monthly Salary (₹)': float(row[9]),
                'Performance Rating': row[10],
                'Work Mode': row[11]
            }
            return jsonify(employee)
        else:
            return jsonify({'message': f'Employee ID {emp_id} not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)})

# 📝 POST API to insert new employee
@app.route('/employees', methods=['POST'])
@require_auth
def add_employee():
    try:
        data = request.get_json()

        insert_query = """
        INSERT INTO [dbo].[OLE DB Destination] (
            [Employee ID], [Full Name], [Gender], [Age], [Department],
            [Designation], [Joining Date], [Location], [Experience (Years)],
            [Monthly Salary (₹)], [Performance Rating], [Work Mode]
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            data['Employee ID'],
            data['Full Name'],
            data['Gender'],
            data['Age'],
            data['Department'],
            data['Designation'],
            data['Joining Date'],
            data['Location'],
            data['Experience (Years)'],
            data['Monthly Salary (₹)'],
            data['Performance Rating'],
            data['Work Mode']
        )

        cursor.execute(insert_query, values)
        conn.commit()

        return jsonify({'message': 'Employee added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)})

# 🔄 PUT API to update employee by string ID
@app.route('/employees/<emp_id>', methods=['PUT'])
@require_auth
def update_employee(emp_id):
    try:
        data = request.get_json()

        update_query = """
        UPDATE [dbo].[OLE DB Destination]
        SET [Full Name] = ?, [Gender] = ?, [Age] = ?, [Department] = ?,
            [Designation] = ?, [Joining Date] = ?, [Location] = ?,
            [Experience (Years)] = ?, [Monthly Salary (₹)] = ?,
            [Performance Rating] = ?, [Work Mode] = ?
        WHERE [Employee ID] = ?
        """

        values = (
            data['Full Name'],
            data['Gender'],
            data['Age'],
            data['Department'],
            data['Designation'],
            data['Joining Date'],
            data['Location'],
            data['Experience (Years)'],
            data['Monthly Salary (₹)'],
            data['Performance Rating'],
            data['Work Mode'],
            emp_id
        )

        cursor.execute(update_query, values)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'message': f'Employee ID {emp_id} not found'}), 404

        return jsonify({'message': f'Employee ID {emp_id} updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})

# 🚀 Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
