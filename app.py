from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from forms import ContactForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from models import db, Project, BlogPost, ContactMessage, NewsletterSubscriber
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '669c000dcb83e30c44c7d5d75ddf627211a689315685976fe1f5c1e00f720c26'  # Change this to a random secret key

# Configuration
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATE_FOLDER'] = 'templates'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Contact Information
app.config['CONTACT_EMAIL'] = os.environ.get('CONTACT_EMAIL', 'contact@example.com')
app.config['CONTACT_PHONE'] = os.environ.get('CONTACT_PHONE', '+1 234 567 890')
app.config['CONTACT_LOCATION'] = os.environ.get('CONTACT_LOCATION', 'New York, USA')
app.config['CONTACT_AVAILABILITY'] = os.environ.get('CONTACT_AVAILABILITY', 'Available for projects')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Import and initialize admin panel
from admin import init_admin

# Initialize Flask-Admin
admin = init_admin(app)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Routes
@app.route('/')
def index():
    """Home page - Personal Portfolio"""
    featured_projects = Project.query.filter_by(featured=True).limit(3).all()
    recent_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('index.html', projects=featured_projects, posts=recent_posts)

@app.route('/contact')
def contact():
    """Contact page"""
    form = ContactForm()
    return render_template('contact.html', 
                         form=form,
                         active_page='contact')

@app.route('/works')
def works():
    """Works/Portfolio page"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    query = Project.query
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Project.title.contains(search) | Project.description.contains(search))
    
    projects = query.order_by(Project.created_at.desc()).all()
    categories = db.session.query(Project.category.distinct()).all()
    
    return render_template('works-simple.html', projects=projects, categories=categories, current_category=category, search_query=search)

@app.route('/works-masonry')
def works_masonry():
    """Works Masonry page"""
    return render_template('works-masonry.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/blog')
def blog():
    """Blog page"""
    page = request.args.get('page', 1, type=int)
    per_page = 5 # Adjust per_page for the main grid

    # Get the most recent featured post
    featured_post = BlogPost.query.filter_by(published=True, featured=True)        .order_by(BlogPost.created_at.desc()).first()

    # Get paginated regular posts, excluding the featured one if it exists
    posts_query = BlogPost.query.filter_by(published=True)
    if featured_post:
        posts_query = posts_query.filter(BlogPost.id != featured_post.id)
    
    posts = posts_query.order_by(BlogPost.created_at.desc())        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('blog-creative.html', featured_post=featured_post, posts=posts)

@app.route('/blog/<slug>')
def blog_article(slug):
    """Blog article page"""
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    related_posts = BlogPost.query.filter(BlogPost.id != post.id, BlogPost.published == True)\
        .order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('blog-article.html', post=post, related_posts=related_posts)

@app.route('/project/<int:project_id>')
def project_details(project_id):
    """Project details page"""
    project = Project.query.get_or_404(project_id)
    related_projects = Project.query.filter(Project.id != project.id, Project.category == project.category)\
        .limit(3).all()
    return render_template('project-details.html', project=project, related_projects=related_projects)

@app.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html')

@app.route('/404')
def error_404():
    """404 Error page"""
    return render_template('404.html')

# Contact form handler
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Create new contact message
            contact = ContactMessage(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
            db.session.add(contact)
            db.session.commit()

            # Send email notification
            msg = Message('New Contact Form Submission',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[app.config['CONTACT_EMAIL']])
            msg.body = f"""
            New contact form submission:
            
            Name: {form.name.data}
            Email: {form.email.data}
            Message: {form.message.data}
            """
            mail.send(msg)

            flash('Thank you! Your message has been sent successfully.', 'success')
        except Exception as e:
            app.logger.error(f'Error in contact form: {str(e)}')
            db.session.rollback()
            flash('Oops! Something went wrong. Please try again later.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('contact'))

# Newsletter subscription handler
@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handle newsletter subscription"""
    email = request.form.get('email')
    
    # Check if email already exists
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        if existing.subscribed:
            return jsonify({'status': 'warning', 'message': 'Email already subscribed!'})
        else:
            existing.subscribed = True
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Successfully resubscribed!'})
    
    # Add new subscriber
    subscriber = NewsletterSubscriber(email=email)
    db.session.add(subscriber)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Successfully subscribed!'})

# Initialize database
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if Project.query.count() == 0:
        sample_projects = [
            Project(
                title="Devpulse AI",
                description="A powerful VS Code extension that leverages Gemini AI to enhance development productivity through intelligent code suggestions, automated documentation, and smart debugging assistance.",
                short_description="VS Code Extension powered by Gemini AI",
                image_url="img/works/preview/Microsoft.VisualStudio.Services.Icons.png",
                tags="VS Code Extension, Gemini AI, Python, JavaScript",
                github_url="https://github.com/",
                live_url="https://marketplace.visualstudio.com/",
                category="web",
                featured=True
            ),
            Project(
                title="Websage AI",
                description="AI-powered web scraping tool that intelligently extracts data from websites using advanced machine learning algorithms.",
                short_description="AI for scraping data from websites",
                image_url="img/works/preview/1200x800_prv-02.webp",
                tags="Flask/Python, JavaScript, AI Agentic",
                github_url="https://github.com/",
                live_url="https://websage-ai.com",
                category="web",
                featured=True
            ),
            Project(
                title="Delivery Service App",
                description="Mobile application for food delivery service with real-time tracking, payment integration, and user management.",
                short_description="Mobile app design",
                image_url="img/works/preview/1200x800_prv-03.webp",
                tags="UI/UX, Mobile, Flutter",
                github_url="https://github.com/",
                live_url="https://delivery-app.com",
                category="mobile",
                featured=True
            )
        ]
        
        for project in sample_projects:
            db.session.add(project)
        
        # Add sample blog posts
        sample_posts = [
            BlogPost(
                title="Frontend innovations and user journeys",
                slug="frontend-innovations-user-journeys",
                content="Exploring the latest trends in frontend development and how they impact user experience design...",
                excerpt="Exploring the latest trends in frontend development and how they impact user experience design.",
                featured_image="img/blog/1000x1250_psec-01.webp",
                tags="Frontend, React, JavaScript",
                published=True,
                featured=True
            ),
            BlogPost(
                title="Branding in creating digital experiences",
                slug="branding-digital-experiences",
                content="How effective branding strategies can enhance digital user experiences and build stronger connections...",
                excerpt="How effective branding strategies can enhance digital user experiences and build stronger connections.",
                featured_image="img/blog/1000x1250_psec-02.webp",
                tags="UI/UX, Design, Branding",
                published=True,
                featured=False
            )
        ]
        
        for post in sample_posts:
            db.session.add(post)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
