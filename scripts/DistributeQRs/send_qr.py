import pandas as pd
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# ─── CONFIG ───────────────────────────────────────────
EXCEL_FILE = "students.xlsx"       # or "students.csv"
QR_FOLDER  = "qrcodes"             # folder containing ID.png files
SMTP_SERVER  = "smtp.office365.com"  # Outlook/Microsoft 365
SMTP_PORT    = 587
# ──────────────────────────────────────────────────────

def send_qr_emails(sender_name: str, sender_email: str):
    # Load the sheet
    if EXCEL_FILE.endswith(".csv"):
        df = pd.read_csv(EXCEL_FILE)
    else:
        df = pd.read_excel(EXCEL_FILE)

    # Login prompt (password never stored in code)
    import getpass
    password = getpass.getpass(f"Enter password for {sender_email}: ")

    # Connect to Outlook SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(sender_email, password)

    success, failed = 0, []

    for _, row in df.iterrows():
        student_id = str(row["ID"]).strip()
        student_email = str(row["Email"]).strip()
        qr_path = os.path.join(QR_FOLDER, f"{student_id}.png")

        if not os.path.exists(qr_path):
            print(f"⚠️  QR not found for ID {student_id}, skipping.")
            failed.append(student_id)
            continue

        # Build email
        msg = MIMEMultipart()
        msg["From"]    = sender_email
        msg["To"]      = student_email
        msg["Subject"] = "Your Attendance QR Code"

        body = f"""Dear Student,

Please find your personal QR code attached to this email.
Keep it safe as it may be required for Attendance.

Regards,
{sender_name}
"""
        msg.attach(MIMEText(body, "plain"))

        # Attach QR image
        with open(qr_path, "rb") as f:
            img = MIMEImage(f.read(), name=f"{student_id}.png")
        msg.attach(img)

        # Send
        try:
            server.sendmail(sender_email, student_email, msg.as_string())
            print(f"✅ Sent to {student_email} (ID: {student_id})")
            success += 1
        except Exception as e:
            print(f"❌ Failed for {student_email}: {e}")
            failed.append(student_id)

    server.quit()
    print(f"\nDone! ✅ {success} sent, ❌ {len(failed)} failed.")
    if failed:
        print("Failed IDs:", failed)

sender_name  = input("Enter your name (e.g. Eng. Ahmed): ").strip()
sender_email = input("Enter your email: ").strip()
send_qr_emails(sender_name=sender_name, sender_email=sender_email)