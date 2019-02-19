from django.core.mail import send_mail, EmailMessage


def send_mail_fun(subject, sms_text, email_to):
    try:
        # print(" i in send email subject : ", subject, " sms_text: ", sms_text, " email_to: ", email_to)
        email = EmailMessage(subject, ''.join(sms_text), to=[email_to])
        email.send()
    except Exception as e:
        print("Exception in email ", e)
