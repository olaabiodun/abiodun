from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, FileField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Optional, URL, NumberRange
from flask_wtf.file import FileField, FileAllowed

class ProjectForm(FlaskForm):
    # Basic Information
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    excerpt = TextAreaField('Excerpt', validators=[Optional()])
    
    # Client Information
    client = StringField('Client', validators=[Optional(), Length(max=100)])
    services = StringField('Services (comma-separated)', validators=[Optional(), Length(max=200)])
    industry = StringField('Industry', validators=[Optional(), Length(max=100)])
    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=300)])
    
    # Challenge Section
    challenge_summary = TextAreaField('Challenge Summary', validators=[Optional()])
    challenge_description = TextAreaField('Challenge Description', validators=[Optional()])
    
    # Solution Section
    solution_summary = TextAreaField('Solution Summary', validators=[Optional()])
    solution_description = TextAreaField('Solution Description', validators=[Optional()])
    
    # Client Feedback
    client_feedback = TextAreaField('Client Feedback', validators=[Optional()])
    client_name = StringField('Client Name', validators=[Optional(), Length(max=100)])
    client_role = StringField('Client Role', validators=[Optional(), Length(max=100)])
    client_company = StringField('Client Company', validators=[Optional(), Length(max=100)])
    client_company_url = StringField('Client Company URL', validators=[Optional(), URL(), Length(max=200)])
    
    # Media and URLs
    image_url = StringField('Image URL', validators=[Optional(), URL(), Length(max=200)])
    github_url = StringField('GitHub URL', validators=[Optional(), URL(), Length(max=200)])
    live_url = StringField('Live URL', validators=[Optional(), URL(), Length(max=200)])
    
    # Metadata
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('design', 'Design'),
        ('branding', 'Branding'),
        ('marketing', 'Marketing'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    featured = BooleanField('Featured Project')
    
    # File Upload (optional for existing projects)
    project_image = FileField('Project Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt', validators=[Optional()])

    # Image upload
    featured_image_url = StringField('Featured Image URL', validators=[Optional(), URL(), Length(max=200)])
    blog_image = FileField('Featured Image Upload', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])

    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=200)])
    published = BooleanField('Published')
    featured = BooleanField('Featured Post')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])

class BlogPostGeneratorForm(FlaskForm):
    name = StringField('Generator Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Optional()])

    # Content generation settings
    topic = StringField('Topic', validators=[DataRequired(), Length(min=1, max=200)])
    keywords = TextAreaField('Keywords (comma-separated)', validators=[Optional()])
    content_type = SelectField('Content Type', choices=[
        ('article', 'Article'),
        ('tutorial', 'Tutorial'),
        ('news', 'News'),
        ('review', 'Review'),
        ('guide', 'Guide')
    ], validators=[DataRequired()])
    writing_style = SelectField('Writing Style', choices=[
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('technical', 'Technical'),
        ('conversational', 'Conversational')
    ], validators=[DataRequired()])
    target_audience = SelectField('Target Audience', choices=[
        ('general', 'General Public'),
        ('developers', 'Developers'),
        ('designers', 'Designers'),
        ('entrepreneurs', 'Entrepreneurs'),
        ('students', 'Students')
    ], validators=[DataRequired()])

    # Scheduling settings
    schedule_type = SelectField('Schedule Type', choices=[
        ('interval', 'Interval (every N hours)'),
        ('once', 'One-time'),
        ('cron', 'Cron Expression')
    ], validators=[DataRequired()])

    interval_hours = IntegerField('Interval Hours', validators=[Optional(), NumberRange(min=1, max=168)])
    scheduled_time = DateTimeField('Scheduled Time', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')

    # Generation settings
    max_length = IntegerField('Max Length (words)', validators=[DataRequired(), NumberRange(min=300, max=5000)], default=1500)
    include_images = BooleanField('Include image suggestions')
    auto_publish = BooleanField('Auto-publish generated posts')

    is_active = BooleanField('Active', default=True)