from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from flask import make_response
import io


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business.db'
app.config['SECRET_KEY'] = 'hardwarebusiness2024'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# OOP - Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')

    def __repr__(self):
        return f'<User {self.username}>'

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<Item {self.name}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f'<Customer {self.name}>'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='jobs')

    def __repr__(self):
        return f'<Job {self.title}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard
@app.route('/')
@login_required
def home():
    item_count = InventoryItem.query.count()
    customer_count = Customer.query.count()
    job_count = Job.query.count()
    pending_count = Job.query.filter_by(status='Pending').count()
    low_stock = InventoryItem.query.filter(InventoryItem.quantity < 10).all()
    return render_template('index.html', item_count=item_count,
                         customer_count=customer_count,
                         job_count=job_count,
                         pending_count=pending_count,
                         low_stock=low_stock)

# Inventory Routes
@app.route('/inventory')
@login_required
def inventory():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    query = InventoryItem.query
    if search:
        query = query.filter(InventoryItem.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    items = query.all()
    categories = db.session.query(InventoryItem.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('inventory.html', items=items,
                         search=search, category=category,
                         categories=categories)

@app.route('/inventory/add', methods=['POST'])
@login_required
def add_item():
    new_item = InventoryItem(
        name=request.form['name'],
        quantity=int(request.form['quantity']),
        price=float(request.form['price']),
        category=request.form['category']
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>')
@login_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.quantity = int(request.form['quantity'])
        item.price = float(request.form['price'])
        item.category = request.form['category']
        db.session.commit()
        return redirect(url_for('inventory'))
    return render_template('edit_item.html', item=item)

# Customer Routes
@app.route('/customers')
@login_required
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customers/add', methods=['POST'])
@login_required
def add_customer():
    new_customer = Customer(
        name=request.form['name'],
        phone=request.form['phone'],
        email=request.form['email']
    )
    db.session.add(new_customer)
    db.session.commit()
    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form['phone']
        customer.email = request.form['email']
        db.session.commit()
        return redirect(url_for('customers'))
    return render_template('edit_customer.html', customer=customer)

# Job Routes
@app.route('/jobs')
@login_required
def jobs():
    all_jobs = Job.query.all()
    all_customers = Customer.query.all()
    return render_template('jobs.html', jobs=all_jobs, customers=all_customers)

@app.route('/jobs/add', methods=['POST'])
@login_required
def add_job():
    new_job = Job(
        title=request.form['title'],
        status=request.form['status'],
        customer_id=request.form['customer_id'] or None
    )
    db.session.add(new_job)
    db.session.commit()
    return redirect(url_for('jobs'))

# Admin only - create staff accounts
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!')
        return redirect(url_for('home'))
    return render_template('register.html')

# Create tables and default admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        
@app.route('/invoice/<int:job_id>')
@login_required
def generate_invoice(job_id):
    job = Job.query.get_or_404(job_id)
    customer = job.customer

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFillColorRGB(0.17, 0.24, 0.31)
    p.rect(0, height-80, width, 80, fill=1)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, height-50, "Hardware Business Manager")
    p.setFont("Helvetica", 12)
    p.drawString(40, height-70, "Invoice / Job Report")

    # Invoice details
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height-120, f"Job: {job.title}")

    p.setFont("Helvetica", 12)
    p.drawString(40, height-150, f"Status: {job.status}")

    if customer:
        p.drawString(40, height-175, f"Customer: {customer.name}")
        p.drawString(40, height-195, f"Phone: {customer.phone or 'N/A'}")
        p.drawString(40, height-215, f"Email: {customer.email or 'N/A'}")

    # Divider
    p.setStrokeColorRGB(0.17, 0.24, 0.31)
    p.setLineWidth(2)
    p.line(40, height-235, width-40, height-235)

    # Footer
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawString(40, 40, "Generated by Hardware Business Manager")

    p.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_job_{job_id}.pdf'
    return response



if __name__ == '__main__':
    app.run(debug=True)
