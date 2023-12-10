
import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
SENDER_ADDRESS=os.environ.get('SENDER_ADDRESS')
SENDER_PASSWORD=os.environ.get('SENDER_PASSWORD')
SMTP_SERVER_ADDRESS=os.environ.get('SMTP_SERVER_ADDRESS')
PORT=os.environ.get('PORT')
subject='You are Shortlisted'
message="Congratulation's!!  You have been shortlisted for the next round. Wish u good luck"
with st.form("Email Form"):
    email = st.text_input(label="Email Id",placeholder="Please enter your email id")
    submit= st.form_submit_button("Submit")
def send_email(sender, password, receiver, smtp_server, smtp_port, email_message, subject):
    message = MIMEMultipart()
    message['To'] = receiver
    message['From']  = sender
    message['Subject'] = subject
    message.attach(MIMEText(email_message,'plain', 'utf-8'))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.ehlo()
    server.login(sender, password)
    text = message.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()
if submit:
    send_email(sender=SENDER_ADDRESS, password=SENDER_PASSWORD, receiver= email, smtp_server=SMTP_SERVER_ADDRESS, smtp_port=PORT, email_message=message, subject=subject)