import requests
from django.template import loader, Context
from django.conf import settings

def send_registration_mail(user):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(settings.ANYMAIL.get('MAILGUN_SENDER_DOMAIN'))
    try:

       template = loader.get_template('email/registration.html')
       
       send_mail = requests.post(request_url, auth=('api',  settings.ANYMAIL.get('MAILGUN_API_KEY')), data={
       'from' : 'vedantbari40@gmail.com',
       'to' : user.email,
       'subject': 'Registration Confirmation',
       'html' : template.render(user.__dict__),
       }
       )
       print(send_mail.text)
    except Exception as e:
       print(e)


def send_otp_mail(user):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(settings.ANYMAIL.get('MAILGUN_SENDER_DOMAIN'))
    try:
       from django.template import loader, Context
       template = loader.get_template('email/login_otp.html')
       import requests
       send_mail = requests.post(request_url, auth=('api',  settings.ANYMAIL.get('MAILGUN_API_KEY')), data={
       'from' : 'vedantbari40@gmail.com',
       'to' : user.email,
       'subject': 'Verification Code',
       'html' : template.render(user.__dict__),
       }
       )
       print(send_mail.text)  
    except Exception as e:
        print("mail exception",e)        