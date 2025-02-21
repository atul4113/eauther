from djangae.mail import AsyncEmailBackend
import logging


class MailError(Exception):
    """
    Raise when there are errors with mail.
    """
    pass


class ManyAddressesInToFieldError(MailError):
    """
    Raise when there are many addresses in TO field.

    In RODO/GDPR regulation, mail addresses are considered personal data and shouldn't be shared with other people.
    To avoid situation where addresses are leaked to unauthorized persons, addresses should be in BCC.
    If there is a need to let know prime recipient that other persons are informed, use CC.
    """
    pass


class RecipientsCheckEmailBackend(AsyncEmailBackend):
    def send_messages(self, email_messages):

        messages_with_many_addresses = [message for message in email_messages if len(message.to) > 1]

        if len(messages_with_many_addresses) > 0:
            logging.error('[Mail] Recipients error - length of TO field more than 1 in {} messages'.format(len(messages_with_many_addresses)))
            raise ManyAddressesInToFieldError("Recipients should be in CC or BCC field")

        return super(RecipientsCheckEmailBackend, self).send_messages(email_messages)
