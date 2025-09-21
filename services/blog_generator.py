import os
import google.generativeai as genai
from datetime import datetime, timedelta
from models import db, BlogPost, BlogPostGenerator
from flask import current_app

class BlogPostGenerationService:
    def __init__(self, api_key=None):
        """Initialize Gemini AI with API key"""
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    def generate_blog_post(self, generator):
        """Generate a blog post using Gemini AI"""
        if not self.model:
            raise Exception("Gemini API key not configured")

        try:
            # Create a detailed prompt for Gemini
            prompt = self._create_generation_prompt(generator)

            # Generate content
            response = self.model.generate_content(prompt)

            if response and response.text:
                # Extract title and content
                title, content = self._parse_generated_content(response.text)

                # Create blog post
                blog_post = BlogPost(
                    title=title,
                    slug=self._create_slug(title),
                    content=content,
                    excerpt=self._generate_excerpt(content),
                    tags=generator.keywords,
                    published=generator.auto_publish,
                    featured=False,
                    featured_image=None  # Could be enhanced to generate image URLs
                )

                # Save to database
                db.session.add(blog_post)
                db.session.commit()

                # Update generator statistics
                generator.last_generated = datetime.utcnow()
                generator.total_generated += 1

                # Calculate next scheduled time
                if generator.schedule_type == 'interval':
                    generator.next_scheduled = datetime.utcnow() + timedelta(hours=generator.interval_hours)
                elif generator.schedule_type == 'once':
                    generator.next_scheduled = None

                db.session.commit()

                return blog_post

            else:
                raise Exception("Failed to generate content from Gemini")

        except Exception as e:
            current_app.logger.error(f"Blog post generation failed: {str(e)}")
            raise

    def _create_generation_prompt(self, generator):
        """Create a detailed prompt for Gemini AI"""
        prompt = f"""
Write a {generator.content_type} about {generator.topic}.

**Writing Style**: {generator.writing_style}
**Target Audience**: {generator.target_audience}
**Maximum Length**: {generator.max_length} words

**Key Requirements**:
- Start with an engaging title
- Write comprehensive, well-researched content
- Include practical examples and actionable insights
- Use clear, engaging language appropriate for the target audience
- Structure with headings and subheadings for easy reading
- Include a compelling introduction and conclusion

**Keywords to include**: {generator.keywords or generator.topic}

**Additional Instructions**:
- Focus on providing value to the reader
- Use storytelling where appropriate
- Include data, statistics, or research findings if relevant
- End with actionable takeaways

Please format your response as:
TITLE: [Your engaging title]
CONTENT: [Your full article content]
"""
        return prompt

    def _parse_generated_content(self, content):
        """Parse the generated content to extract title and body"""
        lines = content.strip().split('\n')
        title = ""
        body_lines = []

        # Find title
        for line in lines:
            if line.upper().startswith('TITLE:'):
                title = line[6:].strip()
                break

        # Find content section
        in_content = False
        for line in lines:
            if line.upper().startswith('CONTENT:'):
                in_content = True
                continue
            elif in_content and line.upper().startswith('TITLE:'):
                break
            elif in_content:
                body_lines.append(line)

        body = '\n'.join(body_lines).strip()
        return title or "Generated Blog Post", body or content

    def _create_slug(self, title):
        """Create a URL-friendly slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug

    def _generate_excerpt(self, content, max_length=200):
        """Generate an excerpt from the content"""
        if not content:
            return ""

        # Remove HTML tags and get plain text
        import re
        text = re.sub(r'<[^>]+>', '', content)

        # Get first few sentences
        sentences = text.split('.')
        excerpt = ""
        for sentence in sentences:
            if len(excerpt + sentence) < max_length:
                excerpt += sentence + '.'
            else:
                break

        return excerpt.strip()[:max_length] + '...' if len(excerpt) > max_length else excerpt.strip()

    def test_connection(self):
        """Test Gemini API connection"""
        if not self.model:
            return False, "API key not configured"

        try:
            response = self.model.generate_content("Say 'Hello' in one word.")
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
