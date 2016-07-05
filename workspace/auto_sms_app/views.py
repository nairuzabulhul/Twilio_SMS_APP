import twilio
from twilio.rest import TwilioRestClient 

from django.contrib.messages import success as success_message
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render

from .forms import SMSForm


def auto_sms(request, send_success=False):
    
    #if this is a POST request we need to process the form data #1
    if request.method == 'POST':
        # Create instance of SMSForm #2
        form = SMSForm(request.POST)
        
        #form validation , if the form is valid, send an SMS message #3
        if form.is_valid():
            if form.send_twilio_message():
                # If the message sends successfully
                success_message(request, 'SMS successfully sent!')
                return redirect('sms_app')

        #after sending the message is sent, return to the template #4
        return render(request, "sms_app_template.html", {
            'form': form,
        })

    # Here we instantiate a blank SMSForm (we don't pass it any data)
    form = SMSForm()  #return a black SMSForm #1
    return render(request, 'sms_app_template.html', {  # render the form #2
      'form': form,
    })
