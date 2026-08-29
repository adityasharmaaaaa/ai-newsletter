import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from newsletter_generator import fetch_weekly_data, generate_markdown_newsletter

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587


def fetch_active_subscribers() -> list:
    """Returns a list of emails for all active subscribers."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM subscribers WHERE is_active = TRUE;")
        rows = cursor.fetchall()
        
        # Unpack the list of tuples returned by psycopg2
        return [row[0] for row in rows]
        
    except Exception as e:
        print(f"Database Error: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# --- 3. DISPATCH LOGIC ---
def dispatch_emails():
    # Step A: Fetch data & generate the deep-dive Markdown content
    print("Generating this week's AI report...")
    weekly_data = fetch_weekly_data()
    md_content = generate_markdown_newsletter(weekly_data)
    
    # Step B: Fetch your audience
    subscribers = fetch_active_subscribers()
    if not subscribers:
        print("No active subscribers found. Aborting dispatch.")
        return
        
    print(f"Preparing to send to {len(subscribers)} subscribers...")

    # Step C: Connect to SMTP and dispatch
    try:
        print(f"Connecting to {SMTP_SERVER}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USER, SMTP_PASS)
        
        for email in subscribers:
            # 1. Construct the email payload
            msg = MIMEMultipart()
            msg["Subject"] = "🚀 Detailed AI Engineering Weekly Report"
            msg["From"] = f"Content Curator Pipeline <{SMTP_USER}>"
            msg["To"] = email
            
            # 2. Add a clean, simple text body
            body_text = (
                "Hello,\n\n"
                "Your weekly AI Engineering deep-dive is ready. "
                "Please find the comprehensive report attached as a Markdown (.md) file, "
                "formatted for easy reading in your IDE, Notion, or Obsidian.\n\n"
                "Best,\n"
                "The Content Curator AI"
            )
            msg.attach(MIMEText(body_text, "plain"))
            
            # 3. Create the Markdown file attachment
            part = MIMEBase("application", "octet-stream")
            # Encode the raw string into bytes so it can be attached
            part.set_payload(md_content.encode('utf-8'))
            
            # 4. Encode the file payload in Base64 for safe email transit
            encoders.encode_base64(part)
            
            # 5. Add headers to tell the email client it is a downloadable file
            part.add_header(
                "Content-Disposition", 
                "attachment; filename=\"AI_Engineering_Report.md\""
            )
            
            # 6. Attach the file to the message
            msg.attach(part)
            
            # 7. Send the email
            server.send_message(msg)
            print(f"✅ Sent successfully to {email}")
            
    except Exception as e:
        print(f"SMTP Error: {e}")
    finally:
        if 'server' in locals():
            server.quit()
            print("Disconnected from SMTP server.")

if __name__ == "__main__":
    dispatch_emails()
