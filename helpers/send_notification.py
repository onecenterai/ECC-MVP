import os
from dotenv import load_dotenv

from pydantic  import EmailStr, BaseModel
from typing import List

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

class Email(BaseModel):
    email: List[EmailStr]


def send_mail(email: Email, location: str, emergency_name:str, agencies):
    try:
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))

        for i, em in enumerate(email.model_dump().get('email')):
            template=f'{emergency_name} at {location} need {agencies[i]}'
            msg = MIMEMultipart()
            msg['From'] = os.getenv('MAIL_USERNAME')
            msg['To'] = em
            msg['Subject'] = 'Test'

            msg.attach(MIMEText(template, 'plain'))

            server.sendmail(os.getenv('MAIL_USERNAME'), em, msg.as_string())

        server.quit()
        return {'Message', 'Notifications has been sent to the agencies successfully. Help is on its way'}

    except Exception as e:
       print(e)
       return {'message': 'Error sending notification'}
    

# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
#     MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
#     MAIL_PORT=587,
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_SSL_TLS=True,
#     MAIL_STARTTLS=True,
#     MAIL_FROM=os.getenv('MAIL_USERNAME'),
#     MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
#     MAIL_DEBUG=True
# )

# async def send_mail(email: Email):
#     try:
#         template='ECC MVP Test'
#         message = MessageSchema(
#             subject='ECC-MVP',
#             recipients=email.model_dump().get('email'),
#             body=template,
#             subtype='html'
#         )

#         fm = FastMail(conf)
#         await fm.send_message(message)
#         return {'message': 'Notification Sent Successfully'}
#     except Exception as e:
#         print(e)
#         return {'message': 'Error sending notification'}
    