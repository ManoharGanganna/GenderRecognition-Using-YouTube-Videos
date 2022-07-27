from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from flask import current_app


def send_email(to_mail):
    print('to_mail',to_mail)
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = current_app.config['MAIL_API_KEY']

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "My Subject"
    html_content = "<html><body><h3>Your results has been processed , Please search again to view results   " \
                   "</h3></body></html> "
    sender = {'name': "No Reply", 'email': 'no-reply@gendertube.com'}
    to = [{'email': to_mail}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
