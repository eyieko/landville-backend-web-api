from django.core.mail import EmailMessage


class EmailHelper:
    """ this class sends emails """

    def send_enquirer_email(data):
        """ send an  email to somebody enquiring about a property """

        email = data[1]
        email2 = data[2]

        subject = "Propery Enquiry"
        body = f"You are receiving this because you have enquired about a \
            property at Landville, a representative from the Client will get \
                to you soon. Thanks for using Landville 😉😉😉😉😉😉😉😉"

        EmailMessage(subject, body, to=[email]).send(
            fail_silently=False)

        subject2 = "An Enquiry about you property"
        body2 = f"Hey {data[3].client.client_name}, somebody is enquiring \
        about your property at LandVille, kindly log into \
         Landville get to know about the enquiry"

        EmailMessage(subject2, body2, to=[email2]).send(
            fail_silently=False)
