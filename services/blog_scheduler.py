from flask_apscheduler import APScheduler
from services.blog_generator import BlogPostGenerationService
from models import db, BlogPostGenerator
from flask import current_app
from datetime import datetime, timedelta

class BlogScheduler:
    def __init__(self, app=None):
        self.app = app
        self.scheduler = APScheduler()
        self.generator_service = BlogPostGenerationService()

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        self.scheduler.init_app(app)

        # Configure scheduler
        app.config.setdefault('SCHEDULER_API_ENABLED', True)
        app.config.setdefault('SCHEDULER_TIMEZONE', 'UTC')

        # Add scheduler endpoints to Flask app
        self.scheduler.start()

    def schedule_blog_generation(self):
        """Schedule blog post generation task"""
        with self.app.app_context():
            try:
                # Get all active generators that should run now
                generators = BlogPostGenerator.query.filter_by(is_active=True).all()

                for generator in generators:
                    if generator.should_generate_now():
                        self._generate_post_for_generator(generator)

            except Exception as e:
                current_app.logger.error(f"Blog generation scheduling failed: {str(e)}")

    def _generate_post_for_generator(self, generator):
        """Generate a blog post for a specific generator"""
        try:
            # Generate the blog post
            blog_post = self.generator_service.generate_blog_post(generator)

            current_app.logger.info(f"Generated blog post: {blog_post.title} for generator: {generator.name}")

        except Exception as e:
            current_app.logger.error(f"Failed to generate post for {generator.name}: {str(e)}")

    def add_generator_job(self, generator):
        """Add a specific job for a generator (for cron-based scheduling)"""
        if generator.schedule_type == 'cron' and generator.cron_expression:
            # For cron-based scheduling, we'd need more complex job management
            # For now, we'll handle this in the main scheduling loop
            pass

    def remove_generator_job(self, generator):
        """Remove scheduled job for a generator"""
        # Implementation for removing specific jobs
        pass

    def get_next_run_time(self, generator):
        """Calculate when a generator should next run"""
        if not generator.is_active:
            return None

        now = datetime.utcnow()

        if generator.schedule_type == 'once' and generator.scheduled_time:
            return generator.scheduled_time if generator.scheduled_time > now else None

        if generator.schedule_type == 'interval' and generator.interval_hours:
            if not generator.last_generated:
                return now
            return generator.last_generated + timedelta(hours=generator.interval_hours)

        return None

    def update_generator_schedules(self):
        """Update next scheduled times for all generators"""
        with self.app.app_context():
            try:
                generators = BlogPostGenerator.query.filter_by(is_active=True).all()

                for generator in generators:
                    next_run = self.get_next_run_time(generator)
                    if next_run != generator.next_scheduled:
                        generator.next_scheduled = next_run
                        db.session.commit()

            except Exception as e:
                current_app.logger.error(f"Failed to update generator schedules: {str(e)}")

# Global scheduler instance
scheduler_instance = None

def get_scheduler():
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = BlogScheduler()
    return scheduler_instance

def init_scheduler(app):
    """Initialize scheduler with Flask app"""
    scheduler = get_scheduler()
    scheduler.init_app(app)

    # Add the main scheduling job
    scheduler.scheduler.add_job(
        func=scheduler.schedule_blog_generation,
        trigger="interval",
        minutes=30,  # Check every 30 minutes
        id='blog_generation_scheduler',
        name='Blog Post Generation Scheduler',
        replace_existing=True
    )

    # Add a job to update generator schedules daily
    scheduler.scheduler.add_job(
        func=scheduler.update_generator_schedules,
        trigger="interval",
        hours=1,  # Update every hour
        id='update_generator_schedules',
        name='Update Generator Schedules',
        replace_existing=True
    )

    return scheduler
