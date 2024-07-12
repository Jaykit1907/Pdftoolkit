from flask import Flask, render_template, request, send_file
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter
import fitz
from fpdf import FPDF
from PIL import Image
import PyPDF2
import os


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

@app.route('/convert', methods=['POST'])

def convert():
    if 'pdfFile' not in request.files:
        return "No PDF file provided"

    pdf_file = request.files['pdfFile']

    if pdf_file.filename == '':
        return "No PDF file selected"

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
    pdf_file.save(pdf_path)

    docx_filename = os.path.splitext(pdf_file.filename)[0] + '.docx'
    docx_path = os.path.join(app.config['DOWNLOAD_FOLDER'], docx_filename)

    convert_pdf_to_docx(pdf_path, docx_path)
    os.remove(pdf_path)
    return send_file(docx_path, as_attachment=True)


def convert_pdf_to_docx(pdf_path, docx_path):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#******************************************************************************************************
@app.route('/hellow', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        return "No file part"

    files = request.files.getlist('files[]')

    uploaded_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            uploaded_files.append(filename)
            
    if len(uploaded_files) < 2:
        return "Please upload at least two PDF files"

    # Merge the uploaded PDF files
    merged_output = os.path.join(app.config['DOWNLOAD_FOLDER'], 'merged_output.pdf')
    merge_pdfs(uploaded_files, merged_output)
    
   
    for file in uploaded_files:
        os.remove(file)
        
    return send_file(merged_output, as_attachment=True)


def merge_pdfs(input_pdfs, output_pdf):
    pdf_merger = PyPDF2.PdfMerger()

    for pdf in input_pdfs:
        with open(pdf, 'rb') as pdf_file:
            pdf_merger.append(pdf_file)

    with open(output_pdf, 'wb') as output_file:
        pdf_merger.write(output_file)


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
        
        
        

#********************************************************************************************************************
                                                        #contactus
# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'pass123'
mysql_database = 'jaykit'

# Connect to MySQL
db = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)

@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone_no= request.form['phone_no']
    message = request.form['message']

    cursor = db.cursor()
    query = "INSERT INTO contactus (first_name,last_name,email,phone_no,message) VALUES (%s, %s, %s,%s,%s)"
    cursor.execute(query, (first_name,last_name,email,phone_no,message))
    db.commit()
    cursor.close()

    return redirect(url_for('contact',message='message sent successfully'))


#********************************************************************************************************************
                                                   #signup
# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pass123',
    'database': 'jaykit'
}

@app.route('/signup_form', methods=['POST'])
def signup_form():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM signup WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return redirect(url_for('signup',message='This Email-Id already exist'))
    
    # If email doesn't exist, insert new user
    cursor.execute("INSERT INTO signup (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)", (first_name, last_name, email, password))
    conn.commit()
    conn.close()
    return redirect(url_for('login',message='Account created Successfully'))



#********************************************************************************************************************
                                                     #login

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pass123',
    'database': 'jaykit'
}

# Function to verify login credentials
def verify_login(email, password):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM signup WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)
        return None


@app.route('/login_form', methods=['POST'])
def login_form():
    email = request.form['email']
    password = request.form['password']

    user = verify_login(email, password)

    if user:
        return redirect(url_for('index', message='Login Successful'))
        
    else:
        return redirect(url_for('login', message='Invalid username or password'))







#********************************************************************************************************************




@app.route('/protect_pdf', methods=['POST'])
def protect_pdf():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    password = request.form['password']

    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_pdffile(file.filename):
        try:
            reader = PdfReader(file)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with open(f'downloads/{file.filename}', 'wb') as f:
                writer.write(f)

            return send_file(f'downloads/{file.filename}', as_attachment=True)
        except Exception as e:
            return str(e)

def allowed_pdffile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

if __name__ == '__main__':
    app.run(debug=True)

