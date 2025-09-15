from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, flash, request, render_template
from models import db, Project, BlogPost, ContactMessage, NewsletterSubscriber

# Custom admin views
class ProjectAdmin(ModelView):
    column_list = ['title', 'category', 'featured', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['category', 'featured', 'created_at']
    form_columns = ('title', 'description', 'short_description', 'image_url', 'tags', 'github_url', 'live_url', 'category', 'featured')
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            flash(f'Project "{model.title}" created successfully!', 'success')
        else:
            flash(f'Project "{model.title}" updated successfully!', 'success')

class BlogPostAdmin(ModelView):
    column_list = ['title', 'published', 'featured', 'created_at']
    column_searchable_list = ['title', 'content']
    column_filters = ['published', 'featured', 'created_at']
    form_columns = ('title', 'slug', 'content', 'excerpt', 'featured_image', 'tags', 'published', 'featured')
    
    def on_model_change(self, form, model, is_created):
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

# Function to initialize admin
def init_admin(app):
    admin = Admin(app, name='Portfolio Admin', template_mode='bootstrap4', url='/admin')
    
    # Add views
    admin.add_view(ProjectAdmin(Project, db.session, name='Projects'))
    admin.add_view(BlogPostAdmin(BlogPost, db.session, name='Blog Posts'))
    admin.add_view(ContactMessageAdmin(ContactMessage, db.session, name='Messages'))
    admin.add_view(NewsletterSubscriberAdmin(NewsletterSubscriber, db.session, name='Subscribers'))
    
    return admin
