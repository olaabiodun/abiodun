from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    project_type = SelectField('Project Type', choices=[
        ('', 'Select a project type'),
        ('web_design', 'Web Design'),
        ('web_development', 'Web Development'),
        ('mobile_app', 'Mobile App'),
        ('consulting', 'Consulting'),
        ('other', 'Other')
    ], validators=[Optional()])
    budget_range = SelectField('Budget Range', choices=[
        ('', 'Select budget range'),
        ('<5k', 'Under $5,000'),
        ('5k-10k', '$5,000 - $10,000'),
        ('10k-25k', '$10,000 - $25,000'),
        ('25k-50k', '$25,000 - $50,000'),
        ('>50k', 'Over $50,000')
    ], validators=[Optional()])
    timeline = StringField('Timeline', validators=[Optional(), Length(max=100)])
    newsletter_signup = BooleanField('Subscribe to newsletter')
    submit = SubmitField('Send Message')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(min=3, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    excerpt = TextAreaField('Excerpt', validators=[Optional(), Length(max=500)])
    client = StringField('Client', validators=[DataRequired(), Length(max=100)])
    services = StringField('Services', validators=[DataRequired()], description='Comma-separated services')
    industry = StringField('Industry', validators=[Optional(), Length(max=100)])
    tags = StringField('Tags', validators=[Optional()], description='Comma-separated tags')
    challenge_summary = TextAreaField('Challenge Summary', validators=[Optional()])
    challenge_description = TextAreaField('Challenge Description', validators=[Optional()])
    solution_summary = TextAreaField('Solution Summary', validators=[Optional()])
    solution_description = TextAreaField('Solution Description', validators=[Optional()])
    client_feedback = TextAreaField('Client Feedback', validators=[Optional()])
    client_name = StringField('Client Name', validators=[Optional(), Length(max=100)])
    client_role = StringField('Client Role', validators=[Optional(), Length(max=100)])
    client_company = StringField('Client Company', validators=[Optional(), Length(max=100)])
    client_company_url = StringField('Client Company URL', validators=[Optional(), Length(max=200)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=500)])
    image_upload = FileField('Upload Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only (jpg, png, webp, gif)!')])
    github_url = StringField('GitHub URL', validators=[Optional(), Length(max=500)])
    live_url = StringField('Live URL', validators=[Optional(), Length(max=500)])
    playstore_url = StringField('Play Store URL', validators=[Optional(), Length(max=500)])
    appstore_url = StringField('App Store URL', validators=[Optional(), Length(max=500)])
    apk_url = StringField('APK URL', validators=[Optional(), Length(max=500)])
    apk_upload = FileField('Upload APK', validators=[FileAllowed(['apk'], 'APK files only!')])
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile App'),
        ('design', 'Design'),
        ('consulting', 'Consulting'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    featured = BooleanField('Featured Project')
    submit = SubmitField('Save Project')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=50)])
    excerpt = TextAreaField('Excerpt', validators=[Optional(), Length(max=500)])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    tags = StringField('Tags', validators=[Optional()], description='Comma-separated tags')
    category = SelectField('Category', choices=[
        ('technology', 'Technology'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('tutorial', 'Tutorial'),
        ('news', 'News'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    featured_image = StringField('Featured Image URL', validators=[Optional(), Length(max=500)])
    published = BooleanField('Published')
    submit = SubmitField('Save Post')

class NewsletterForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(max=100)])
    preferences = SelectField('Content Preferences', choices=[
        ('all', 'All Content'),
        ('projects', 'Projects Only'),
        ('blog', 'Blog Posts Only'),
        ('news', 'News & Updates')
    ], default='all')
    submit = SubmitField('Subscribe')