import email.utils
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(SUBJECT, BODY_TEXT="", BODY_HTML="", ATTACHMENT=""):
    # Replace sender@example.com with your "From" address.
    # This address must be verified.
    SENDER = "hselimozturk@gmail.com"
    SENDERNAME = "Selim"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENTS = ["hselimozturk@gmail.com", "fatih@narmoni.com.tr"]

    # Replace smtp_username with your Amazon SES SMTP user name.
    USERNAME_SMTP = "AKIAY6PTD7ASTPO7EI7D"

    # Replace smtp_password with your Amazon SES SMTP password.
    PASSWORD_SMTP = "BBLsWkwFI4/IhnDW9yNrgXW9PpndVBERaxilF6IIYNno"

    # (Optional) the name of a configuration set to use for this message.
    # If you comment out this line, you also need to remove or comment out
    # the "X-SES-CONFIGURATION-SET:" header below.
    # CONFIGURATION_SET = "ConfigSet"

    # If you're using Amazon SES in an AWS Region other than US West (Oregon),
    # replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
    # endpoint in the appropriate region.
    HOST = "email-smtp.eu-central-1.amazonaws.com"
    PORT = 587

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = email.utils.formataddr((SENDERNAME, SENDER))
    # Comment or delete the next line if you are not using a configuration set
    # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(BODY_TEXT, "plain")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    if BODY_HTML:
        part2 = MIMEText(BODY_HTML, "html")
        msg.attach(part2)

    if ATTACHMENT:
        att = MIMEApplication(open(ATTACHMENT, "rb").read())
        att.add_header(
            "Content-Disposition", "attachment", filename=os.path.basename(ATTACHMENT)
        )
        msg.attach(att)

    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.

    # Try to send the message.
    try:
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        # stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        for RECIPIENT in RECIPIENTS:
            msg["To"] = RECIPIENT
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as e:
        print("Error: ", e)
    else:
        print("Email sent!")


if __name__ == "__main__":
    import os
    from services import json_util

    dirname = os.path.dirname(__file__)
    test_path = os.path.join(dirname, "test.txt")
    json_util.save_json(test_path, {"hi": "hallo"})
    send_email("test att", ATTACHMENT=test_path)
