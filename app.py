import os
from flask import Flask, render_template, request, Response
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

# AWS S3 credentials from environment variables
ACCESS_KEY = os.getenv('AKIAWAEROK6AUT3IEUHI')
SECRET_KEY = os.getenv('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')
BUCKET_NAME = os.getenv('portfolio-website-48')

# Initialize boto3 S3 client
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY)

# ... rest of your app code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit/email', methods=['POST'])
def submit():
    # Get form data
    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    email = request.form['email']
    linkedin = request.form['linkedin']
    github = request.form['github']
    objective = request.form['objective']
    institution_names = request.form.getlist('institution_name[]')
    branch_names = request.form.getlist('branch_name[]')
    start_years = request.form.getlist('start_year[]')
    percentages = request.form.getlist('percentage[]')
    skills = request.form.getlist('skills[]')
    certifications = request.form.getlist('certifications[]')
    projects = request.form.getlist('projects[]')
    work_experience_years = request.form.getlist('work_experience_years[]')
    work_experience_companies = request.form.getlist('work_experience_company[]')
    work_experience_descriptions = request.form.getlist('work_experience_description[]')

    # Get image file
    image = request.files['image']
    image_key = f'{full_name.replace(" ", "_")}_profile_picture.jpg'

    # Upload image to S3
    try:
        s3.upload_fileobj(image, BUCKET_NAME, image_key, ExtraArgs={'ACL': 'public-read'})
        image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{image_key}"
    except NoCredentialsError:
        return 'AWS credentials not found.'

    # Debug prints
    print("Name:", full_name)
    print("Education:", institution_names, branch_names, start_years, percentages)

    # Create HTML content
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body>
    <!-- TITLE -->
    <div style="display: flex; align-items: center;">
    <!-- Profile Picture -->
    <img src="{image_url}" alt="Profile Picture" style="max-width: 200px; max-height: 200px; border-radius: 5px; margin-right: 20px;">

    <!-- Profile Information -->
    <div>
        <h1><strong>{full_name}</strong></h1>
        <i class="fa fa-envelope"></i> {email}<br>
        <i class="fa fa-phone-square"></i> {phone_number}<br>
        <i class="fa fa-linkedin"></i> <a href="{linkedin}" target="_blank">LinkedIn</a><br>
        <i class="fa fa-github"></i> <a href="{github}" target="_blank">GitHub</a>
    </div>
</div><br>

    <hr style="border: 2px solid black;">
    <!-- OBJECTIVE -->
<section>
    <h3><strong>OBJECTIVE</strong></h3>
    <hr>
    <p>&emsp;{objective}</p>
</section>


    <!-- Work -->
    <section>
        <h3><strong>WORK EXPERIENCE</strong></h3>
        <hr>
        <ul>
            {"".join([f"<li>{work_experience_companies[i]}  [{work_experience_years[i]}] <br>   Description: {work_experience_descriptions[i]}</li>" for i in range(len(work_experience_years))])}
        </ul>
    <section>

    <!-- PROJECTS -->
    <section>
        
        <h3><strong>PROJECTS</strong></h3>
        <hr>
        <ul>
            {"".join([f"<li>{project}</li>" for project in projects])}
        </ul>
    </section>

    <!-- EDUCATION -->
    <section>
        
        <h3><strong>EDUCATION</strong></h3>
        <hr>
        <ul>
            {"".join([f"<li>{institution_names[i]}<br>{branch_names[i]}<br>{start_years[i]}<br>{percentages[i]}</li>" for i in range(len(institution_names))])}
        </ul>
    </section>

    <!-- CERTIFICATIONS -->
    <section>
        
        <h3>CERTIFICATIONS</h3>
        <hr>
        <ul>
            {"".join([f"<li>{certification}</li>" for certification in certifications])}
        </ul>
    </section>

    <!-- SKILLS -->
    <section>
        
        <h3><strong>SKILLS:</strong></h3>
        <hr>
        <ul>
            {"".join([f"<li>{skill}</li>" for skill in skills])}
        </ul>
    </section>

</body>
</html>
"""

    # Upload to S3 and handle errors
    try:
        s3.put_object(Body=content, Bucket=BUCKET_NAME, Key='resume.html', ContentType='text/html')
        return 'Uploaded successfully!'
    except NoCredentialsError:
        return 'AWS credentials not found.'

@app.route('/download/email')
def download():
    # Download file from S3
    try:
        s3.download_file(BUCKET_NAME, 'resume.html', 'resume.html')
        with open('resume.html', 'rb') as f:
            return Response(f.read(), mimetype='text/html', headers={"Content-Disposition": "attachment;filename=resume.html"})
    except NoCredentialsError:
        return 'AWS credentials not found.'

if __name__ == '__main__':
    app.run(debug=True)