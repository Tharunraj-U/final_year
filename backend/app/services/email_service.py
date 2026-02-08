"""
Email Service for sending weekly reports and notifications.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import json


class EmailService:
    def __init__(self):
        self.email_user = os.getenv('EMAIL_USER')
        self.email_pass = os.getenv('EMAIL_PASS')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send an email with HTML content."""
        if not self.email_user or not self.email_pass:
            print("Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"CodeMaster AI <{self.email_user}>"
            msg['To'] = to_email
            
            # Add plain text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.sendmail(self.email_user, to_email, msg.as_string())
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def generate_weekly_report_html(self, user_data: dict, stats: dict, submissions: list):
        """Generate HTML content for weekly report."""
        user_name = user_data.get('name', 'Coder')
        problems_solved = stats.get('problems_solved', 0)
        avg_score = stats.get('avg_score', 0)
        streak = stats.get('streak', 0)
        total_submissions = len(submissions)
        
        # Calculate this week's progress
        week_ago = datetime.now() - timedelta(days=7)
        week_submissions = [s for s in submissions if s.get('timestamp', '') > week_ago.isoformat()]
        week_problems = len(set(s.get('problem_id') for s in week_submissions))
        
        # Get top topics
        topic_counts = {}
        for sub in week_submissions:
            topic = sub.get('topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        top_topics = sorted(topic_counts.items(), key=lambda x: -x[1])[:3]
        
        topics_html = ""
        for topic, count in top_topics:
            topics_html += f'<li style="margin: 5px 0;">{topic.replace("_", " ").title()} - {count} problems</li>'
        
        if not topics_html:
            topics_html = '<li style="margin: 5px 0;">No problems solved this week</li>'
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🧠 CodeMaster AI</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Weekly Progress Report</p>
        </div>
        
        <!-- Main Content -->
        <div style="background: white; padding: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hi {user_name}! 👋</h2>
            <p style="color: #666; line-height: 1.6;">Here's your weekly coding progress summary:</p>
            
            <!-- Stats Grid -->
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 25px 0;">
                <div style="flex: 1; min-width: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: white;">{week_problems}</div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 12px;">Problems This Week</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: white;">{problems_solved}</div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 12px;">Total Solved</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%); border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: white;">{streak}🔥</div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 12px;">Day Streak</div>
                </div>
            </div>
            
            <!-- Average Score -->
            <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #333;">📊 Average Score</h3>
                <div style="background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {avg_score}%; border-radius: 10px;"></div>
                </div>
                <p style="margin: 10px 0 0 0; color: #666;">{avg_score}% average score across all submissions</p>
            </div>
            
            <!-- Top Topics -->
            <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #333;">🎯 Topics Practiced This Week</h3>
                <ul style="margin: 0; padding-left: 20px; color: #666;">
                    {topics_html}
                </ul>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.frontend_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 15px 40px; border-radius: 30px; font-weight: bold; font-size: 16px;">
                    Continue Practicing →
                </a>
            </div>
            
            <!-- Motivational Message -->
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 12px; padding: 20px; text-align: center;">
                <p style="margin: 0; color: #8b4513; font-size: 16px;">
                    💪 <strong>Keep up the great work!</strong> Consistency is key to mastering coding.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
            <p>You're receiving this because you're registered on CodeMaster AI.</p>
            <p>© 2026 CodeMaster AI - Your AI-Powered Learning Assistant</p>
        </div>
    </div>
</body>
</html>
'''
        return html
    
    def send_weekly_report(self, user_data: dict, stats: dict, submissions: list):
        """Send weekly progress report to a user."""
        email = user_data.get('email')
        if not email:
            print(f"No email for user {user_data.get('user_id')}")
            return False
        
        html_content = self.generate_weekly_report_html(user_data, stats, submissions)
        subject = f"📊 Your Weekly Coding Report - {datetime.now().strftime('%B %d, %Y')}"
        
        text_content = f"""
Hi {user_data.get('name', 'Coder')}!

Here's your weekly coding progress:
- Problems solved: {stats.get('problems_solved', 0)}
- Average score: {stats.get('avg_score', 0)}%
- Current streak: {stats.get('streak', 0)} days

Keep practicing at {self.frontend_url}

Best,
CodeMaster AI Team
"""
        
        return self.send_email(email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
