from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_caching import Cache
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from forms import ProjectForm, BlogForm, ContactForm
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Configure cache
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',  # In-memory cache
    'CACHE_DEFAULT_TIMEOUT': 60,  # 1 minute cache timeout
    'CACHE_THRESHOLD': 1000  # Maximum number of items the cache will store
})
cache.init_app(app)

def make_cache_key(*args, **kwargs):
    """Create a cache key from the request path and query parameters."""
    path = request.path     
    args_pairs = [(k, v) for k, v in request.args.items()]
    args_pairs.sort()
    return f"{path}:{json.dumps(args_pairs)}"

load_dotenv()

app.secret_key = '669c000dcb83e30c44c7d5d75ddf627211a689315685976fe1f5c1e00f720c26'

supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Routes
@app.route('/')
@cache.cached(timeout=60, key_prefix='index_page')  # Cache for 1 minute
def index():
    try:
        # Try to get projects from cache first
        projects = cache.get('projects_list')
        if projects is None:
            response = supabase.table('projects').select('*').execute()
            projects = response.data if response.data else []
            cache.set('projects_list', projects, timeout=60)  # Cache for 1 minute
            
        # Try to get blogs from cache
        blogs = cache.get('blogs_list')
        if blogs is None:
            response = supabase.table('blog_posts').select('*').order('created_at', desc=True).limit(3).execute()
            blogs = response.data if response.data else []
            cache.set('blogs_list', blogs, timeout=60)  # Cache for 1 minute
            
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}")
        projects = []
        blogs = []
        
    return render_template('index.html', projects=projects, blogs=blogs)

@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        p_res = supabase.table('projects').select('id', count='exact').execute()
        project_count = p_res.count if p_res.count is not None else len(p_res.data)
        b_res = supabase.table('blog_posts').select('id', count='exact').execute()
        blog_count = b_res.count if b_res.count is not None else len(b_res.data)
        c_res = supabase.table('contacts').select('id', count='exact').execute()
        contact_count = c_res.count if c_res.count is not None else len(c_res.data)
    except Exception as e:
        current_app.logger.error(f"Dashboard stats error: {e}")
        project_count = blog_count = contact_count = 0
    return render_template('admin/dashboard.html', project_count=project_count, blog_count=blog_count, contact_count=contact_count)

@app.route('/contact')
def contact():
    form = ContactForm()
    return render_template('contact.html', form=form, active_page='contact')

@app.route('/works')
@cache.cached(timeout=60, key_prefix='works_page')  # Cache for 1 minute
def works():
    try:
        projects = cache.get('all_projects')
        if projects is None:
            response = supabase.table('projects').select('*').execute()
            projects = response.data if response.data else []
            cache.set('all_projects', projects, timeout=60)  # Cache for 1 minute
    except Exception as e:
        current_app.logger.error(f"Error fetching works projects: {e}")
        projects = []
    return render_template('works-simple.html', projects=projects)

@app.route('/works-masonry')
def works_masonry():
    # For simplicity, reuse works view
    return works()

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-conditions')
def terms_conditions():
    return render_template('terms-conditions.html')

@app.route('/blog')
@cache.cached(timeout=1, key_prefix=make_cache_key)
def blog():
    try:
        # Try to get blog posts from cache first
        cache_key = 'blog_posts_all'
        posts = cache.get(cache_key)
        
        if posts is None:
            response = supabase.table('blog_posts').select('*').order('created_at', desc=True).execute()
            posts = response.data if response.data else []
            
            # Convert created_at strings to datetime objects
            for post in posts:
                if isinstance(post.get('created_at'), str):
                    try:
                        post['created_at'] = datetime.fromisoformat(post['created_at'])
                    except Exception:
                        pass
            
            # Cache the processed posts
            cache.set(cache_key, posts, timeout=600)  # Cache for 10 minutes
        
        # Assume first post as featured if exists
        featured_post = posts[0] if posts else None
        
    except Exception as e:
        current_app.logger.error(f"Error fetching blog posts: {e}")
        posts = []
        featured_post = None
        
    return render_template('blog-creative.html', featured_post=featured_post, posts=posts)

@app.route('/blog/<slug>')
def blog_article(slug):
    try:
        # Try to get the article from cache
        cache_key = f'blog_article_{slug}'
        post = cache.get(cache_key)
        
        if post is None:
            post_resp = supabase.table('blog_posts').select('*').eq('slug', slug).execute()
            post = post_resp.data[0] if post_resp.data else None
            
            if post and isinstance(post.get('created_at'), str):
                try:
                    post['created_at'] = datetime.fromisoformat(post['created_at'])
                except Exception:
                    pass
            
            if post:  # Only cache if we found the post
                cache.set(cache_key, post, timeout=60)  # Cache for 1 minute
        
        # Get related posts (cached separately)
        related_cache_key = 'related_posts_all'
        related_posts = cache.get(related_cache_key)
        
        if related_posts is None:
            related_resp = supabase.table('blog_posts').select('*').neq('slug', slug).order('created_at', desc=True).limit(3).execute()
            related_posts = related_resp.data if related_resp.data else []
            
            # Convert dates for related posts
            for p in related_posts:
                if p and isinstance(p.get('created_at'), str):
                    try:
                        p['created_at'] = datetime.fromisoformat(p['created_at'])
                    except Exception:
                        pass
            
            cache.set(related_cache_key, related_posts, timeout=60)  # Cache for 1 minute
        
        # Get previous and next posts for navigation
        all_posts_resp = supabase.table('blog_posts').select('id, slug, title, created_at').order('created_at', desc=True).execute()
        all_posts = all_posts_resp.data if all_posts_resp.data else []
        
        # Find current post index
        current_index = next((i for i, p in enumerate(all_posts) if p['id'] == post['id']), -1)
        
        # Get previous and next posts
        prev_post = all_posts[current_index + 1] if current_index < len(all_posts) - 1 else None
        next_post = all_posts[current_index - 1] if current_index > 0 else None
        
    except Exception as e:
        current_app.logger.error(f"Error fetching blog article: {e}")
        post = None
        related_posts = []
        prev_post = None
        next_post = None
    
    return render_template('blog-article.html', 
                         post=post, 
                         related_posts=related_posts,
                         prev_post=prev_post,
                         next_post=next_post)

@app.route('/project/<project_id>')
def project_details(project_id):
    try:
        # Get the current project
        proj_resp = supabase.table('projects').select('*').eq('id', project_id).execute()
        project = proj_resp.data[0] if proj_resp.data else None
        
        if project:
            # Convert created_at to datetime if it's a string
            if isinstance(project.get('created_at'), str):
                try:
                    project['created_at'] = datetime.fromisoformat(project['created_at'])
                except Exception:
                    pass
            
            # Get all projects ordered by created_at (newest first)
            all_projects_resp = supabase.table('projects').select('id, slug, title, created_at').order('created_at', desc=True).execute()
            all_projects = all_projects_resp.data if all_projects_resp.data else []
            
            # Find current project index
            current_index = next((i for i, p in enumerate(all_projects) if p['id'] == project['id']), -1)
            
            # Get previous and next projects
            prev_project = all_projects[current_index + 1] if current_index < len(all_projects) - 1 else None
            next_project = all_projects[current_index - 1] if current_index > 0 else None
            
            # Get related projects (excluding current and nav projects)
            related_ids = {p['id'] for p in [prev_project, next_project] if p}
            related_ids.add(project['id'])
            related_resp = supabase.table('projects')\
                .select('*')\
                .not_.in_('id', list(related_ids))\
                .limit(3)\
                .execute()
            related_projects = related_resp.data if related_resp.data else []
            
            # Convert created_at for related projects
            for rp in related_projects:
                if isinstance(rp.get('created_at'), str):
                    try:
                        rp['created_at'] = datetime.fromisoformat(rp['created_at'])
                    except Exception:
                        pass
        else:
            prev_project = None
            next_project = None
            related_projects = []
            
    except Exception as e:
        current_app.logger.error(f"Error fetching project details: {e}")
        project = None
        related_projects = []
        prev_project = None
        next_project = None
        
    return render_template('project-details.html', 
                         project=project, 
                         related_projects=related_projects,
                         prev_project=prev_project,
                         next_project=next_project)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/404')
def error_404():
    return render_template('404.html')

# Contact form handler
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_data = {
            'name': form.name.data,
            'email': form.email.data,
            'subject': form.subject.data if hasattr(form, 'subject') else 'Contact Form Submission',
            'message': form.message.data,
            'phone': form.phone.data if hasattr(form, 'phone') else '',
            'company': form.company.data if hasattr(form, 'company') else '',
            'project_type': form.project_type.data if hasattr(form, 'project_type') else '',
            'budget_range': form.budget_range.data if hasattr(form, 'budget_range') else '',
            'timeline': form.timeline.data if hasattr(form, 'timeline') else '',
            'newsletter_signup': form.newsletter_signup.data if hasattr(form, 'newsletter_signup') else False
        }
        
        try:
            result = supabase.table('contacts').insert(contact_data).execute()
            if hasattr(result, 'error') and result.error:
                return jsonify({'success': False, 'message': str(result.error)}), 400
            return jsonify({'success': True, 'message': 'Thank you for your message! We will get back to you soon.'})
        except Exception as e:
            current_app.logger.error(f"Error saving contact: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred while saving your message.'}), 500
    else:
        return jsonify({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors in the form.'
        })

# Newsletter subscription handler
@app.route('/subscribe', methods=['POST'])
def subscribe():
    return jsonify({'status': 'info', 'message': 'Subscription logic removed.'})

# Admin Project Routes
@app.route('/admin/projects')
def admin_projects():
    try:
        resp = supabase.table('projects').select('*').order('created_at', desc=True).execute()
        projects = resp.data if resp.data else []
    except Exception as e:
        flash(f"Error fetching projects: {e}", "error")
        projects = []
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
def admin_add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project_data = {
            'title': form.title.data,
            'slug': form.slug.data,
            'description': form.description.data,
            'excerpt': form.excerpt.data,
            'client': form.client.data,
            'services': [s.strip() for s in form.services.data.split(',')] if form.services.data else [],
            'industry': form.industry.data,
            'tags': [t.strip() for t in form.tags.data.split(',')] if form.tags.data else [],
            'challenge_summary': form.challenge_summary.data,
            'challenge_description': form.challenge_description.data,
            'solution_summary': form.solution_summary.data,
            'solution_description': form.solution_description.data,
            'client_feedback': form.client_feedback.data,
            'client_name': form.client_name.data,
            'client_role': form.client_role.data,
            'client_company': form.client_company.data,
            'client_company_url': form.client_company_url.data,
            'image_url': form.image_url.data,
            'github_url': form.github_url.data,
            'live_url': form.live_url.data,
            'category': form.category.data,
            'featured': form.featured.data,
        }
        try:
            supabase.table('projects').insert(project_data).execute()
            flash('Project added successfully!', 'success')
            return redirect(url_for('admin_projects'))
        except Exception as e:
            if "10035" in str(e):
                flash('Project added successfully! (Socket warning ignored)', 'success')
                return redirect(url_for('admin_projects'))
            flash(f'Error adding project: {str(e)}', 'error')
    return render_template('admin/project_form.html', form=form, project=None)

@app.route('/admin/projects/<project_id>/edit', methods=['GET', 'POST'])
def admin_edit_project(project_id):
    try:
        resp = supabase.table('projects').select('*').eq('id', project_id).execute()
        if not resp.data:
            flash('Project not found', 'error')
            return redirect(url_for('admin_projects'))
        project = resp.data[0]
        form = ProjectForm()
        if form.validate_on_submit():
            update_data = {
                'title': form.title.data,
                'slug': form.slug.data,
                'description': form.description.data,
                'excerpt': form.excerpt.data,
                'client': form.client.data,
                'services': [s.strip() for s in form.services.data.split(',')] if form.services.data else [],
                'industry': form.industry.data,
                'tags': [t.strip() for t in form.tags.data.split(',')] if form.tags.data else [],
                'challenge_summary': form.challenge_summary.data,
                'challenge_description': form.challenge_description.data,
                'solution_summary': form.solution_summary.data,
                'solution_description': form.solution_description.data,
                'client_feedback': form.client_feedback.data,
                'client_name': form.client_name.data,
                'client_role': form.client_role.data,
                'client_company': form.client_company.data,
                'client_company_url': form.client_company_url.data,
                'image_url': form.image_url.data,
                'github_url': form.github_url.data,
                'live_url': form.live_url.data,
                'category': form.category.data,
                'featured': form.featured.data,
            }
            try:
                supabase.table('projects').update(update_data).eq('id', project_id).execute()
                flash('Project updated successfully!', 'success')
                return redirect(url_for('admin_projects'))
            except Exception as e:
                if "10035" in str(e):
                    flash('Project updated successfully! (Socket warning ignored)', 'success')
                    return redirect(url_for('admin_projects'))
                flash(f'Error updating project: {str(e)}', 'error')
        # Populate form on GET
        if request.method == 'GET':
            for field in form:
                if field.name in project and project[field.name] is not None:
                    if field.name in ['tags', 'services'] and isinstance(project[field.name], list):
                        field.data = ', '.join(project[field.name])
                    else:
                        field.data = project[field.name]
        return render_template('admin/project_form.html', form=form, project=project)
    except Exception as e:
        flash(f'Error loading project: {str(e)}', 'error')
        return redirect(url_for('admin_projects'))

@app.route('/admin/projects/<project_id>/delete', methods=['POST'])
def admin_delete_project(project_id):
    try:
        supabase.table('projects').delete().eq('id', project_id).execute()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        if "10035" in str(e):
            flash('Project deleted successfully! (Socket warning ignored)', 'success')
        else:
            flash(f'Error deleting project: {str(e)}', 'error')
    return redirect(url_for('admin_projects'))

# Admin Blog Routes (list, add, edit, delete) – simplified placeholders
@app.route('/admin/blogs')
def admin_blogs():
    try:
        resp = supabase.table('blog_posts').select('*').order('created_at', desc=True).execute()
        blogs = resp.data if resp.data else []
    except Exception as e:
        flash(f"Error fetching blogs: {e}", "error")
        blogs = []
    return render_template('admin/blogs.html', blogs=blogs)

@app.route('/admin/blogs/add', methods=['GET', 'POST'])
def admin_add_blog():
    form = BlogForm()
    if form.validate_on_submit():
        blog_data = {
            'title': form.title.data,
            'slug': form.slug.data,
            'content': form.content.data,
            'excerpt': form.excerpt.data,
            'author': form.author.data,
            'category': form.category.data,
            'tags': [t.strip() for t in form.tags.data.split(',')] if form.tags.data else [],
            'featured_image': form.featured_image.data,
            'published': form.published.data,
        }
        try:
            supabase.table('blog_posts').insert(blog_data).execute()
            flash('Blog added successfully!', 'success')
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            if "10035" in str(e):
                flash('Blog added successfully! (Socket warning ignored)', 'success')
                return redirect(url_for('admin_blogs'))
            flash(f'Error adding blog: {str(e)}', 'error')
    return render_template('admin/blog_form.html', form=form, post=None)

@app.route('/admin/blogs/<blog_id>/edit', methods=['GET', 'POST'])
def admin_edit_blog(blog_id):
    try:
        resp = supabase.table('blog_posts').select('*').eq('id', blog_id).execute()
        if not resp.data:
            flash('Blog post not found', 'error')
            return redirect(url_for('admin_blogs'))
        post = resp.data[0]
        form = BlogForm()
        if form.validate_on_submit():
            update_data = {
                'title': form.title.data,
                'slug': form.slug.data,
                'content': form.content.data,
                'excerpt': form.excerpt.data,
                'author': form.author.data,
                'category': form.category.data,
                'tags': [t.strip() for t in form.tags.data.split(',')] if form.tags.data else [],
                'featured_image': form.featured_image.data,
                'published': form.published.data,
            }
            try:
                supabase.table('blog_posts').update(update_data).eq('id', blog_id).execute()
                flash('Blog post updated successfully!', 'success')
                return redirect(url_for('admin_blogs'))
            except Exception as e:
                if "10035" in str(e):
                    flash('Blog post updated successfully! (Socket warning ignored)', 'success')
                    return redirect(url_for('admin_blogs'))
                flash(f'Error updating blog: {str(e)}', 'error')
        # Populate form on GET
        if request.method == 'GET':
            for field in form:
                if field.name in post and post[field.name] is not None:
                    if field.name == 'tags' and isinstance(post[field.name], list):
                        field.data = ', '.join(post[field.name])
                    else:
                        field.data = post[field.name]
        return render_template('admin/blog_form.html', form=form, post=post)
    except Exception as e:
        flash(f'Error loading blog post: {str(e)}', 'error')
        return redirect(url_for('admin_blogs'))

@app.route('/admin/blogs/<blog_id>/delete', methods=['POST'])
def admin_delete_blog(blog_id):
    try:
        supabase.table('blog_posts').delete().eq('id', blog_id).execute()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        if "10035" in str(e):
            flash('Blog post deleted successfully! (Socket warning ignored)', 'success')
        else:
            flash(f'Error deleting blog post: {str(e)}', 'error')
    return redirect(url_for('admin_blogs'))

# Admin Contact Routes
@app.route('/admin/contacts')
def admin_contacts():
    try:
        resp = supabase.table('contacts').select('*').order('created_at', desc=True).execute()
        contacts = resp.data if resp.data else []
    except Exception as e:
        flash(f"Error fetching contacts: {e}", "error")
        contacts = []
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/contacts/<contact_id>/delete', methods=['POST'])
def admin_delete_contact(contact_id):
    try:
        supabase.table('contacts').delete().eq('id', contact_id).execute()
        flash('Message deleted successfully!', 'success')
    except Exception as e:
        if "10035" in str(e):
            flash('Message deleted successfully! (Socket warning ignored)', 'success')
        else:
            flash(f'Error deleting message: {str(e)}', 'error')
    return redirect(url_for('admin_contacts'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
