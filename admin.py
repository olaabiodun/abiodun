import os
from werkzeug.utils import secure_filename
from flask import current_app
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, flash, request, render_template
from models import db, Project, BlogPost, ContactMessage, NewsletterSubscriber, BlogPostGenerator
from forms import ProjectForm, BlogPostForm, BlogPostGeneratorForm
class ProjectAdmin(ModelView):
    column_list = ['title', 'client', 'category', 'featured', 'created_at']
    column_searchable_list = ['title', 'description', 'client', 'industry']
    column_filters = ['category', 'featured', 'industry', 'created_at']
    form_columns = [
        # Basic Information
        'title', 'slug', 'description', 'excerpt',

        # Client Information
        'client', 'services', 'industry', 'tags',

        # Challenge Section
        'challenge_summary', 'challenge_description',

        # Solution Section
        'solution_summary', 'solution_description',

        # Client Feedback
        'client_feedback', 'client_name', 'client_role', 'client_company', 'client_company_url',

        # Media and URLs
        'image_url', 'github_url', 'live_url',

        # Metadata
        'category', 'featured'
    ]
    # Create form with custom template and validation
    form = ProjectForm

    # Custom form template for better organization
    form_widget_args = {
        'description': {'rows': 4},
        'excerpt': {'rows': 3},
        'challenge_summary': {'rows': 3},
        'challenge_description': {'rows': 5},
        'solution_summary': {'rows': 3},
        'solution_description': {'rows': 5},
        'client_feedback': {'rows': 4},
    }

    def on_model_change(self, form, model, is_created):
        # Handle image upload
        if form.project_image.data:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.static_folder, 'img', 'works', 'preview')
            os.makedirs(upload_dir, exist_ok=True)

            # Save uploaded file
            filename = secure_filename(form.project_image.data.filename)
            file_path = os.path.join(upload_dir, filename)
            form.project_image.data.save(file_path)

            # Update model with new image path
            model.image_url = f'/static/img/works/preview/{filename}'

        if is_created:
            flash(f'Project "{model.title}" created successfully!', 'success')
        else:
            flash(f'Project "{model.title}" updated successfully!', 'success')

    def on_form_prefill(self, form, id):
        # Pre-fill form with existing data
        pass

class BlogPostAdmin(ModelView):
    column_list = ['title', 'published', 'featured', 'created_at']
    column_searchable_list = ['title', 'content']
    column_filters = ['published', 'featured', 'created_at']
    form_columns = ('title', 'slug', 'content', 'excerpt', 'featured_image', 'tags', 'published', 'featured')

    # Use custom form with image upload
    form = BlogPostForm

    # Custom form widget args for better layout
    form_widget_args = {
        'content': {'rows': 8},
        'excerpt': {'rows': 4},
    }

    def on_model_change(self, form, model, is_created):
        # Handle image upload
        if form.blog_image.data:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.static_folder, 'img', 'blog')
            os.makedirs(upload_dir, exist_ok=True)

            # Save uploaded file
            filename = secure_filename(form.blog_image.data.filename)
            file_path = os.path.join(upload_dir, filename)
            form.blog_image.data.save(file_path)

            # Update model with new image path
            model.featured_image = f'/static/img/blog/{filename}'

        if is_created:
            flash(f'Blog post "{model.title}" created successfully!', 'success')
        else:
            flash(f'Blog post "{model.title}" updated successfully!', 'success')

class ContactMessageAdmin(ModelView):
    column_list = ['name', 'email', 'read', 'created_at']
    column_searchable_list = ['name', 'email', 'message']
    column_filters = ['read', 'created_at']
    can_create = False
    can_edit = False
    can_delete = True
    
    def mark_as_read(self, ids):
        for id in ids:
            message = ContactMessage.query.get(id)
            if message:
                message.read = True
        db.session.commit()
        flash('Messages marked as read!', 'success')
        return redirect(url_for('contactmessage.index_view'))

class NewsletterSubscriberAdmin(ModelView):
    column_list = ['email', 'subscribed', 'created_at']
    column_searchable_list = ['email']
    column_filters = ['subscribed', 'created_at']
    form_columns = ('email', 'subscribed')

class BlogPostGeneratorAdmin(ModelView):
    column_list = ['name', 'topic', 'schedule_type', 'is_active', 'total_generated', 'last_generated', 'next_scheduled']
    column_searchable_list = ['name', 'topic', 'keywords']
    column_filters = ['is_active', 'schedule_type', 'content_type', 'writing_style']
    form_columns = [
        'name', 'description',
        'topic', 'keywords', 'content_type', 'writing_style', 'target_audience',
        'schedule_type', 'interval_hours', 'scheduled_time',
        'max_length', 'include_images', 'auto_publish', 'is_active'
    ]

    # Use custom form
    form = BlogPostGeneratorForm

    # Custom form widget args
    form_widget_args = {
        'description': {'rows': 3},
        'keywords': {'rows': 2},
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            flash(f'Blog post generator "{model.name}" created successfully!', 'success')
        else:
            flash(f'Blog post generator "{model.name}" updated successfully!', 'success')

    def get_query(self):
        return super().get_query()

    def get_count_query(self):
        return super().get_count_query()

# Function to initialize admin
def init_admin(app):
    admin = Admin(app, name='Portfolio Admin', template_mode='bootstrap4', url='/admin')

    # Add views
    admin.add_view(ProjectAdmin(Project, db.session, name='Projects'))
    admin.add_view(BlogPostAdmin(BlogPost, db.session, name='Blog Posts'))
    admin.add_view(ContactMessageAdmin(ContactMessage, db.session, name='Messages'))
    admin.add_view(NewsletterSubscriberAdmin(NewsletterSubscriber, db.session, name='Subscribers'))
    admin.add_view(BlogPostGeneratorAdmin(BlogPostGenerator, db.session, name='Blog Generators'))

    return admin
