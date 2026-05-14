from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business.db'

db = SQLAlchemy(app)

# OOP - Each class represents a table in the database
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

@app.route('/')
def home():
    item_count = InventoryItem.query.count()
    customer_count = Customer.query.count()
    job_count = Job.query.count()
    pending_count = Job.query.filter_by(status='Pending').count()
    return render_template('index.html', item_count=item_count, 
                         customer_count=customer_count, 
                         job_count=job_count, 
                         pending_count=pending_count)


# Create all tables
with app.app_context():
    db.create_all()

from flask import Flask, render_template, request, redirect, url_for

@app.route('/inventory')
def inventory():
    items = InventoryItem.query.all()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])
    category = request.form['category']
    
    new_item = InventoryItem(name=name, quantity=quantity, price=price, category=category)
    db.session.add(new_item)
    db.session.commit()
    
    return redirect(url_for('inventory'))

@app.route('/customers')
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    
    new_customer = Customer(name=name, phone=phone, email=email)
    db.session.add(new_customer)
    db.session.commit()
    
    return redirect(url_for('customers'))

@app.route('/jobs')
def jobs():
    all_jobs = Job.query.all()
    all_customers = Customer.query.all()
    return render_template('jobs.html', jobs=all_jobs, customers=all_customers)

@app.route('/jobs/add', methods=['POST'])
def add_job():
    title = request.form['title']
    status = request.form['status']
    customer_id = request.form['customer_id'] or None
    
    new_job = Job(title=title, status=status, customer_id=customer_id)
    db.session.add(new_job)
    db.session.commit()
    
    return redirect(url_for('jobs'))



if __name__ == '__main__':
    app.run(debug=True)

