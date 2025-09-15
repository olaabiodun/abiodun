# Portfolio Website - Flask Version

A beautiful, modern portfolio website converted from HTML to Flask while preserving all design elements and functionality.

## 🚀 Features

- **Responsive Design**: Fully responsive across all devices
- **Modern UI/UX**: Clean, professional design with smooth animations
- **Multiple Pages**: Home, About, Portfolio, Blog, Contact, FAQ, and more
- **Interactive Elements**: GSAP animations, parallax effects, and smooth scrolling
- **Contact Form**: Working contact form with Flask backend
- **Newsletter Subscription**: Email subscription functionality
- **SEO Optimized**: Proper meta tags and structured data

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── run.py                 # Development server runner
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── contact.html      # Contact page
│   ├── about-me.html     # About page
│   ├── works-simple.html # Portfolio page
│   ├── works-masonry.html # Portfolio masonry layout
│   ├── blog-creative.html # Blog listing
│   ├── blog-article.html  # Blog article
│   ├── project-details.html # Project details
│   ├── faq.html          # FAQ page
│   └── 404.html          # 404 error page
└── static/               # Static assets
    ├── css/              # Stylesheets
    ├── js/               # JavaScript files
    ├── img/              # Images and icons
    ├── fonts/            # Font files
    └── video/            # Video files
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python app.py
   ```

4. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

## 📱 Available Pages

- **Home** (`/`) - Main portfolio landing page
- **About** (`/about`) - About me page with skills and experience
- **Portfolio** (`/works`) - Project showcase in grid layout
- **Portfolio Masonry** (`/works-masonry`) - Project showcase in masonry layout
- **Blog** (`/blog`) - Blog articles and insights
- **Contact** (`/contact`) - Contact form and information
- **FAQ** (`/faq`) - Frequently asked questions
- **Project Details** (`/project-details`) - Individual project showcase

## 🎨 Design Features

- **Modern Typography**: Clean, readable fonts with proper hierarchy
- **Smooth Animations**: GSAP-powered animations and transitions
- **Interactive Elements**: Hover effects, parallax scrolling, and micro-interactions
- **Dark/Light Mode**: Built-in theme switcher
- **Mobile-First**: Responsive design that works on all devices
- **Performance Optimized**: Optimized images and efficient code

## 🔧 Customization

### Updating Content

1. **Personal Information**: Edit the base template (`templates/base.html`) to update your name, email, and social links
2. **Projects**: Modify the portfolio templates (`templates/works-simple.html`, `templates/works-masonry.html`)
3. **Blog Posts**: Update the blog templates (`templates/blog-creative.html`, `templates/blog-article.html`)
4. **About Section**: Edit `templates/about-me.html` with your information

### Styling

- **CSS Files**: Located in `static/css/`
- **Main Styles**: `static/css/main.min.css`
- **Custom Styles**: Add your custom CSS in the base template

### Images

- **Portfolio Images**: Add your project images to `static/img/works/preview/`
- **Profile Images**: Update avatar images in `static/img/avatars/`
- **Hero Images**: Replace hero images in `static/img/hero/`

## 📧 Contact Form

The contact form is fully functional and includes:

- **Form Validation**: Client-side and server-side validation
- **Email Integration**: Ready for email service integration
- **Success/Error Messages**: User feedback for form submissions
- **CSRF Protection**: Built-in security features

To enable email sending, update the `submit_contact` function in `app.py` with your email service configuration.

## 🚀 Deployment

### Local Development

```bash
python run.py
```

### Production Deployment

For production deployment, consider using:

- **Heroku**: Easy deployment with Procfile
- **DigitalOcean**: VPS deployment
- **AWS**: EC2 or Elastic Beanstalk
- **Google Cloud**: App Engine or Compute Engine

### Environment Variables

Create a `.env` file for production settings:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAIL_SERVER=your-mail-server
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

## 🐛 Troubleshooting

### Common Issues

1. **Flask not found**: Run `pip install -r requirements.txt`
2. **Static files not loading**: Check file paths in templates
3. **Template errors**: Verify Jinja2 syntax in template files
4. **Port already in use**: Change port in `app.py` or `run.py`

### Debug Mode

The application runs in debug mode by default. To disable:

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 📄 License

This project is for personal use. Please respect the original template's license terms.

## 🤝 Support

If you encounter any issues or need help customizing the portfolio:

1. Check the troubleshooting section above
2. Review the Flask documentation
3. Ensure all dependencies are installed correctly

## 🎉 Success!

Your portfolio website is now running on Flask! The design has been completely preserved while adding the power and flexibility of a Python web framework.

Enjoy your new portfolio website! 🚀


