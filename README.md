# Hardware Business Manager
A full-stack web application built to digitalise the operations of a hardware and 
contracting business, replacing manual WhatsApp and spreadsheet workflows 
with a centralised, secure management system.

# The Problem & Solution
Small businesses in the Caribbean typically manage 
inventory, customers and jobs through WhatsApp 
messages and basic spreadsheets which leads to lost 
records, stock mismanagement and poor communication 
between staff.
A secure, role-based web application that gives the 
business one centralised place to manage everything 
in real time.

# Features
- **Login System**: Secure authentication with role-based access (Admin and Staff)
- **Staff Management**: Admin can create and manage staff accounts
- **Inventory Management**: Add, edit, delete and search stock items with category filtering
- **Low Stock Alerts**: Automatic warnings on dashboard and inventory when items fall below 10 units
- **Customer Management**: Store and manage customer contact information
- **Job Tracking**: Create jobs linked to customers with Pending, In Progress and Completed status
- **PDF Invoice Generation**: Download professional invoices for any job
- **Live Dashboard**: Real-time overview of inventory, customers, jobs and pending work

# Tech Stack
 Backend: Python, Flask
 Database: SQLite, SQLAlchemy ORM 
 Authentication: Flask-Login, Werkzeug 
 PDF Generation: ReportLab 
 Frontend: HTML, CSS 
 Architecture: OOP, MVC, RESTful Routes 
 Version Control: Git, GitHub 

# How to Run
**Clone the repository**  
git clone https://github.com/anushkad-code/hardware-business-manager.git

**Navigate into the project**  
cd hardware-business-manager

**Create and activate virtual environment**  
python -m venv venv
source venv/Scripts/activate

**Install dependencies**  
pip install flask flask-sqlalchemy flask-login werkzeug reportlab

**Run the application**  
py app.py
Then open `http://127.0.0.1:5000` in your browser.

Default login:
- **Username:* admin
- **Password:* admin123

# Future Enhancements
- Customer billing with itemised PDF receipts
- Invoice history and records
- Mobile responsive design
- Search and filter across all pages
- Sales reporting and analytics

## 👤 Author
**Anushka Dwarika**  
2nd Year Computer Science with Management Student  
University of the West Indies, St. Augustine  
📍 Trinidad and Tobago 
