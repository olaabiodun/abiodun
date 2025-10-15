from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from forms import ContactForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_caching import Cache
from flask_compress import Compress
from models import db, Project, BlogPost, ContactMessage, NewsletterSubscriber
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '669c000dcb83e30c44c7d5d75ddf627211a689315685976fe1f5c1e00f720c26'  # Change this to a random secret key

# Performance and Optimization Configuration
app.config['CACHE_TYPE'] = os.environ.get('CACHE_TYPE', 'simple')
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
app.config['COMPRESS_ENABLED'] = os.environ.get('COMPRESS_ENABLED', 'True').lower() == 'true'

# CDN Configuration
CDN_URL = os.environ.get('CDN_URL', '')
if CDN_URL:
    app.config['STATIC_URL_PATH'] = CDN_URL
    from flask import url_for
    @app.context_processor
    def override_url_for():
        return dict(url_for=cdn_url_for)

def cdn_url_for(endpoint, **values):
    """Generate CDN URLs for static files"""
    if endpoint == 'static':
        if CDN_URL:
            return CDN_URL.rstrip('/') + url_for(endpoint, **values)
    return url_for(endpoint, **values)

# Database optimization
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'pool_size': 10,
    'max_overflow': 20
}

# Contact Information
app.config['CONTACT_EMAIL'] = os.environ.get('CONTACT_EMAIL', 'contact@example.com')
app.config['CONTACT_PHONE'] = os.environ.get('CONTACT_PHONE', '+1 234 567 890')
app.config['CONTACT_LOCATION'] = os.environ.get('CONTACT_LOCATION', 'New York, USA')
app.config['CONTACT_AVAILABILITY'] = os.environ.get('CONTACT_AVAILABILITY', 'Available for projects')

# Email configuration
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATE_FOLDER'] = 'templates'
# Handle both PostgreSQL and SQLite database URLs
uri = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
# Fix for Render's PostgreSQL URL format
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Initialize performance extensions
cache = Cache(app)
compress = Compress(app)

# Import and initialize admin panel
from admin import init_admin

# Initialize Flask-Admin
admin = init_admin(app)

# Import and initialize blog scheduler
from services.blog_scheduler import init_scheduler

# Initialize blog post generation scheduler
blog_scheduler = init_scheduler(app)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Routes
@app.route('/')
@cache.cached(timeout=300)  # Cache for 5 minutes
def index():
    """Home page - Personal Portfolio"""
    featured_projects = Project.query.filter_by(featured=True).limit(3).all()
    recent_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('index.html', projects=featured_projects, posts=recent_posts)

@app.route('/admin/')
def admin_dashboard():
    stats = {
        'total_projects': Project.query.count(),
        'featured_projects': Project.query.filter_by(featured=True).count(),
        # Add more stats as needed
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/contact')
def contact():
    """Contact page"""
    form = ContactForm()
    return render_template('contact.html', 
                         form=form,
                         active_page='contact')

@app.route('/works')
@cache.cached(timeout=300)
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
@cache.cached(timeout=300)
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
@cache.cached(timeout=300)
def blog_article(slug):
    """Blog article page"""
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    related_posts = BlogPost.query.filter(BlogPost.id != post.id, BlogPost.published == True)\
        .order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('blog-article.html', post=post, related_posts=related_posts)

@app.route('/project/<int:project_id>')
@cache.cached(timeout=300)
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

# Blog generation routes
@app.route('/admin/generate-blog-post/<int:generator_id>')
def generate_blog_post(generator_id):
    """Manually trigger blog post generation for a specific generator"""
    from services.blog_generator import BlogPostGenerationService

    try:
        generator = BlogPostGenerator.query.get_or_404(generator_id)
        if not generator.is_active:
            flash(f'Generator "{generator.name}" is not active', 'error')
            return redirect(url_for('blogpostgenerator.index_view'))

        service = BlogPostGenerationService()
        blog_post = service.generate_blog_post(generator)

        flash(f'Successfully generated blog post: "{blog_post.title}"', 'success')
        return redirect(url_for('blogpost.index_view'))

    except Exception as e:
        flash(f'Error generating blog post: {str(e)}', 'error')
        return redirect(url_for('blogpostgenerator.index_view'))

@app.route('/admin/test-gemini')
def test_gemini():
    """Test Gemini API connection"""
    from services.blog_generator import BlogPostGenerationService

    try:
        service = BlogPostGenerationService()
        success, message = service.test_connection()

        if success:
            flash(f'Gemini API connection successful: {message}', 'success')
        else:
            flash(f'Gemini API connection failed: {message}', 'error')

    except Exception as e:
        flash(f'Error testing Gemini API: {str(e)}', 'error')

@app.route('/health')
@cache.cached(timeout=60)
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'cache_enabled': cache is not None,
        'compression_enabled': compress is not None
    })

@app.route('/performance')
def performance_stats():
    """Performance statistics endpoint"""
    stats = {
        'cache_hits': cache.get('cache_hits', 0),
        'cache_misses': cache.get('cache_misses', 0),
        'total_requests': cache.get('total_requests', 0)
    }
    return jsonify(stats)
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if Project.query.count() == 0:
        sample_projects = [
            Project(
                title="Devpulse AI",
                slug="devpulse-ai",
                description="A powerful VS Code extension that leverages Gemini AI to enhance development productivity through intelligent code suggestions, automated documentation, and smart debugging assistance.",
                excerpt="VS Code Extension powered by Gemini AI",
                client="Tech Startup Inc.",
                services="AI Integration, VS Code Extension Development, API Development",
                industry="Technology",
                tags="VS Code Extension, Gemini AI, Python, JavaScript",
                challenge_summary="Developers needed an AI-powered coding assistant that could understand context and provide intelligent suggestions within VS Code.",
                challenge_description="The main challenge was integrating Gemini AI seamlessly into the VS Code environment while maintaining performance and providing accurate, context-aware suggestions across multiple programming languages.",
                solution_summary="Built a comprehensive VS Code extension with real-time AI assistance.",
                solution_description="Developed a robust extension architecture that leverages Gemini AI's capabilities to provide intelligent code completion, documentation generation, and debugging assistance. The solution includes real-time code analysis, multi-language support, and seamless integration with existing development workflows.",
                client_feedback="The AI integration has significantly improved our development team's productivity. The intelligent suggestions and automated documentation features have reduced development time by 40%.",
                client_name="Sarah Johnson",
                client_role="CTO",
                client_company="Tech Startup Inc.",
                client_company_url="https://techstartup.com",
                image_url="/static/img/works/preview/Microsoft.VisualStudio.Services.Icons.png",
                github_url="https://github.com/example/devpulse-ai",
                live_url="https://marketplace.visualstudio.com/items?itemName=devpulse-ai",
                category="web",
                featured=True
            ),
            Project(
                title="Websage AI",
                slug="websage-ai",
                description="AI-powered web scraping tool that intelligently extracts data from websites using advanced machine learning algorithms.",
                excerpt="AI for scraping data from websites",
                client="Data Analytics Corp",
                services="AI Development, Web Scraping, Machine Learning, Data Processing",
                industry="Data Analytics",
                tags="Flask/Python, JavaScript, AI Agentic",
                challenge_summary="Need for intelligent web scraping that can handle dynamic content and complex data structures.",
                challenge_description="Traditional web scraping tools couldn't handle modern websites with dynamic content, anti-bot measures, and complex data structures. We needed an AI-powered solution that could understand website layouts and extract data intelligently.",
                solution_summary="Developed an AI-powered web scraping platform with intelligent data extraction.",
                solution_description="Created Websage AI, a comprehensive web scraping platform that uses machine learning to understand website structures, handle dynamic content, and extract data intelligently. The platform includes anti-detection measures, data validation, and export capabilities in multiple formats.",
                client_feedback="Websage AI has revolutionized our data collection process. The intelligent scraping capabilities and anti-detection features have improved our success rate by 85%.",
                client_name="Michael Chen",
                client_role="Head of Data",
                client_company="Data Analytics Corp",
                client_company_url="https://data-analytics-corp.com",
                image_url="/static/img/works/preview/1200x800_prv-02.webp",
                github_url="https://github.com/example/websage-ai",
                live_url="https://websage-ai.com",
                category="web",
                featured=True
            ),
            Project(
                title="Delivery Service App",
                slug="delivery-service-app",
                description="Mobile application for food delivery service with real-time tracking, payment integration, and user management.",
                excerpt="Mobile app design for food delivery",
                client="QuickEats Delivery",
                services="Mobile App Development, UI/UX Design, Payment Integration",
                industry="Food Delivery",
                tags="UI/UX, Mobile, Flutter, Firebase",
                challenge_summary="Create a seamless food delivery experience with real-time tracking and easy payment options.",
                challenge_description="The food delivery market is highly competitive, requiring an app that offers exceptional user experience, real-time order tracking, secure payment processing, and efficient delivery management. The challenge was to build an intuitive interface that works perfectly for both customers and delivery drivers.",
                solution_summary="Designed and developed a comprehensive mobile app for food delivery services.",
                solution_description="Created a feature-rich mobile application with real-time GPS tracking, integrated payment systems, user-friendly interface, and comprehensive order management. The app includes customer app, driver app, and admin panel with real-time analytics and reporting.",
                client_feedback="The app has exceeded our expectations. The real-time tracking and intuitive interface have significantly improved customer satisfaction and operational efficiency.",
                client_name="Emma Rodriguez",
                client_role="Operations Manager",
                client_company="QuickEats Delivery",
                client_company_url="https://quickeats.com",
                image_url="/static/img/works/preview/1200x800_prv-03.webp",
                github_url="https://github.com/example/delivery-app",
                live_url="https://delivery-app-demo.com",
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
