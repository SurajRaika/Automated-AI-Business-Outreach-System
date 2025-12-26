import argparse
import subprocess
import sys
import os

def send_email(recipient, subject, html_file, sender=None):
    if not os.path.exists(html_file):
        print(f"❌ HTML file '{html_file}' not found.")
        sys.exit(1)

    with open(html_file, 'r') as f:
        html_content = f.read()

    # Construct the email content
    email_content = f"Subject: {subject}\n"
    email_content += "MIME-Version: 1.0\n"
    email_content += "Content-Type: text/html; charset=utf-8\n"
    if sender:
        email_content += f"From: {sender}\n"
    email_content += f"To: {recipient}\n\n"
    email_content += html_content

    try:
        # Use msmtp to send the email
        # msmtp must be configured on the system
        process = subprocess.run(
            ["msmtp", "-t"],
            input=email_content.encode('utf-8'),
            capture_output=True,
            check=True
        )
        print(f"✅ Email sent successfully to {recipient}!")
        if process.stdout:
            print("msmtp stdout:", process.stdout.decode('utf-8'))
        if process.stderr:
            print("msmtp stderr:", process.stderr.decode('utf-8'))

    except FileNotFoundError:
        print("❌ Error: msmtp command not found. Please ensure msmtp is installed and configured.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error sending email: {e}")
        print("msmtp stdout:", e.stdout.decode('utf-8'))
        print("msmtp stderr:", e.stderr.decode('utf-8'))
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Send styled HTML emails via msmtp using an HTML file as the body."
    )
    parser.add_argument("recipient", help="Email address of the recipient")
    parser.add_argument("subject", help="Subject line of the email")
    parser.add_argument("html_file", help="Path to HTML file for email body")
    parser.add_argument("--sender", help="Sender email (must match msmtp config)")

    args = parser.parse_args()

    send_email(args.recipient, args.subject, args.html_file, args.sender)

if __name__ == "__main__":
    main()
