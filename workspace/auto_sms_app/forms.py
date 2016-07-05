# Nairuz: I changed the order of the imports to match standard practice,
#         which is...

# Do imports from the Python lib first

# Then, import from third-party packages
import twilio
from twilio.rest import TwilioRestClient
from twilio.rest.exceptions import TwilioRestException
from twilio.rest.lookups import TwilioLookupsClient

# Then, import Django functions
from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# Finally, import from local Python modules (if any)

#Import credentials from settings.py to verify the phone number 
lookup_client = TwilioLookupsClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

class SMSForm(forms.Form): 
    
    #Create form fields with man and min length, labels are the same as the names in the template ##1
    client_number1 = forms.CharField(label='client_number1', min_length=3,  max_length=3, required=True) 
    client_number2 = forms.CharField(label='client_number2', min_length=3,  max_length=3, required=True)
    client_number3 = forms.CharField(label="client_number3", min_length=4,  max_length=4, required=True)
    message       = forms.CharField(label='message')
    
    def clean(self):
        """Since the client number fields depend on one-another, we will override the form's
           clean() method to perform validation across the three fields.
        """
        # Call the parent class `clean()` method to perform default validation of the fields
        cleaned_data = super(SMSForm, self).clean() ##3 
        
        #get data from the fields #4
        try:
            client_number_field1 = cleaned_data['client_number1']
            client_number_field2 = cleaned_data['client_number2']
            client_number_field3 = cleaned_data['client_number3']
        except KeyError as e:
            # If there are any key errors, then one of the above was not complete.
            raise forms.ValidationError('Please enter a complete, 10-digit US phone number.')
        
        client_number = client_number_field1 + client_number_field2 + client_number_field3 ##5 

        #Validate client's phone number using Twilio lookup library ##6
        try:
            validate_number = lookup_client.phone_numbers.get(client_number, include_carrier_info=True)
            self.cleaned_data['client_number'] = validate_number.phone_number
        except TwilioRestException as e: 
            #Invalid phone number error ##7
            raise forms.ValidationError("This is not a valid US phone number. Please try again.")
        
        return cleaned_data

    def send_twilio_message(self):
        """Use Twilio to send a text message to the phone number provided by the user in this form.

           :return: True if message sends successfully, False if send message fails for any reason.
                    Failures will be added to the form's non-field errors.
        """
        # add three fields tother ##1
        # client_number = self.cleaned_data['client_number1'] + self.cleaned_data['client_number2'] + self.cleaned_data['client_number3']
        client_number = self.cleaned_data['client_number']
        message       = self.cleaned_data ['message'] # message ##2 
        
        try:
            #Create an SMS message  ##2
            return client.messages.create(
             from_ = settings.TWILIO_PHONE_NUMBER,
             to    = client_number,
             body  = message      
            )
            return True
        except TwilioRestException as e:
            # Report form-level errors, if Twilio fails to send the SMS for some reason.
            if e.code == 21608:
                # Code 21608 indicates a phone number that has not been verified            
                self.add_error(None,
                               _('SMS could not be sent the phone number '
                                 'provided has not been verified with Twilio.'))
            else:
                # General message for any other failure to connect to Twilio or send the SMS.
                self.add_error(None,
                               _('Error connecting with Twilio. Your phone number is valid '
                                 'but we could not connect to Twilio at this time. '
                                 'Please try again later.'))
            return False
