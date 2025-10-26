import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_account_email(to_email: str, customer_name: str, account_number: str, account_type: str, balance: float):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "scarydare13@gmail.com"
    app_password = "fnry mkco peif sjtz"  # generated in Gmail

    # Create email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = "Your New Bank Account Details"

    body = f"""
    Dear {customer_name},

    Your {account_type} account has been successfully created.

    Account Number: {account_number}
    Initial Balance: {balance}

    Thank you for banking with us!
    """
    message.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
