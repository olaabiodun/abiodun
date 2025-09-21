from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    client = db.Column(db.String(100), index=True)
    services = db.Column(db.String(200))  # Comma-separated services
    industry = db.Column(db.String(100), index=True)
    tags = db.Column(db.String(300))  # Comma-separated tags
    
    # Challenge section
    challenge_summary = db.Column(db.Text)
    challenge_description = db.Column(db.Text)
    
    # Solution section
    solution_summary = db.Column(db.Text)
    solution_description = db.Column(db.Text)
    
    # Client feedback section
    client_feedback = db.Column(db.Text)
    client_name = db.Column(db.String(100))
    client_role = db.Column(db.String(100))
    client_company = db.Column(db.String(100))
    client_company_url = db.Column(db.String(200))
    
    # Media and URLs
    image_url = db.Column(db.String(300))
    github_url = db.Column(db.String(200))
    live_url = db.Column(db.String(200))
    
    # Metadata
    category = db.Column(db.String(50), default='web', index=True)  # web, mobile, design, etc.
    featured = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    
    def get_services_list(self):
        return [service.strip() for service in self.services.split(',')] if self.services else []

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    tags = db.Column(db.String(200))
    published = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPostGenerator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Content generation settings
    topic = db.Column(db.String(200), nullable=False)
    keywords = db.Column(db.Text)  # Comma-separated keywords
    content_type = db.Column(db.String(50), default='article')  # article, tutorial, news, etc.
    writing_style = db.Column(db.String(100), default='professional')  # professional, casual, technical, etc.
    target_audience = db.Column(db.String(100), default='general')  # developers, designers, general, etc.

    # Scheduling settings
    schedule_type = db.Column(db.String(20), default='interval')  # interval, cron, once
    interval_hours = db.Column(db.Integer, default=24)  # Generate every N hours
    cron_expression = db.Column(db.String(100))  # For cron-based scheduling
    scheduled_time = db.Column(db.DateTime)  # For one-time generation

    # Status and control
    is_active = db.Column(db.Boolean, default=True)
    last_generated = db.Column(db.DateTime)
    next_scheduled = db.Column(db.DateTime)
    total_generated = db.Column(db.Integer, default=0)

    # Generation settings
    max_length = db.Column(db.Integer, default=1500)  # Maximum words per post
    include_images = db.Column(db.Boolean, default=False)
    auto_publish = db.Column(db.Boolean, default=False)  # Auto-publish generated posts

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_keywords_list(self):
        return [kw.strip() for kw in self.keywords.split(',')] if self.keywords else []

    def should_generate_now(self):
        """Check if this generator should run now based on its schedule"""
        if not self.is_active:
            return False

        now = datetime.utcnow()

        if self.schedule_type == 'once' and self.scheduled_time:
            return self.scheduled_time <= now and not self.last_generated

        if self.schedule_type == 'interval' and self.interval_hours:
            if not self.last_generated:
                return True
            return now >= self.last_generated + timedelta(hours=self.interval_hours)

        return False
