from src.auth.email import MailTaskSchema


def user_mail_event(payload: MailTaskSchema):
    # TODO: Configurate SMTP for sending emails to users
    # Now just printing verify token in server console
    print(f'[ Mail Schema ]: {payload}')
    