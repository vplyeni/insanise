from django.core.mail import send_mail

from backend import settings


def send(to_addr, subject, content):
    context = {}
    """ 
    if to_addr and subject and content:
        try:
            send_mail(subject=subject, message=content, from_email=settings.EMAIL_HOST, recipient_list=[to_addr])
            context['message'] = "Mail sent successfully"
        except Exception as e:
            context['message'] = f'Error sending email: {e}'
    else:
        context['message'] = 'All fields are required'
    """
    return context
