"""
Travi 

Copyright Jess Lampe 2016.

Borrowed the lambda function from the Amazon favorite color skill sample and customized for travi needs
"""

from __future__ import print_function

import urllib2
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
#import lxml.etree as ET
import json
from datetime import datetime
from BeautifulSoup import BeautifulSoup 

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, reprompt_text, should_end_session, title=None, card_output=None):
    if title == None and card_output == None:
        output = {'outputSpeech': {
                'type': 'PlainText',
                'text': output
                },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }
        print(output)
        return  output
    else:
        output = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
                },
            'card': {
            'type': 'Simple',
            'title': title,
            'content': card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
        }
        print(output)
        return output


def build_response(session_attributes, speechlet_response):
    print(session_attributes)
    print(speechlet_response)
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Travel Warning"
    speech_output = "Travel Warning. " \
                    "Check to see if there are state department travel warnings for a country. " \
                    "What country do you want to check on?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "What country was that?"
    should_end_session = False
    text_output = "Remember, enroll in the Smart Traveler Enrollment Program (STEP) to receive security messages and make it easier to locate you in an emergency."
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session, card_title, text_output))

def get_error_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    speech_output = "What country was that?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask me about another country by saying, " \
                                "is england safe?" 
    should_end_session = False
    text_output = None
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    speech_output = "Happy travels."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        speech_output, None, should_end_session))

def get_country_warning(intent, session):
    """ 
    receives country, asks State Department for list of countries with warnings
    """
    if 'CountryOne' not in intent['slots']:
        return get_error_response()
    if 'value' not in intent['slots']['CountryOne']:
        return get_error_response()


    country = intent['slots']['CountryOne']['value'].lower()
    print(country)

    if country in countries:
        interest_country = intent['slots']['CountryOne']['value']
        card_title = interest_country
        print(interest_country)
        session_attributes = get_country_warning_from_rss(interest_country)
        should_end_session = False
        print("made it here")

        if session_attributes:
            publish_date = session_attributes['publish_date']
            summary = session_attributes['summary']
            speech_output = "There is a travel warning for " + \
                            interest_country + " since " + session_attributes["publish_date"] +\
                            ". " + summary + \
                            " Do you want to hear the full report?" 
            text_output = session_attributes["full_report"][:7500] + \
                        "... for additional travel warning information for " + \
                        interest_country + " go to the State Department website"
            reprompt_text = "Check on state department travel warnings by asking " \
                        "is england safe?"
        else:
            speech_output = "There is no travel warning for " + \
                            interest_country + \
                            ". What other country would you like to check on?"
            text_output = "There is no travel warning for " + \
                            interest_country
            reprompt_text = "You can ask me about another country by saying, " \
                            "is england safe?" 
    else:
        return get_error_response()
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session, card_title, text_output))

def get_full_report(intent, session):
    should_end_session = False
    session_attributes = {}
    if 'attributes' not in session:
        return get_error_response()
    
    session_attributes = session['attributes']

    if 'country' not in session_attributes:
        return get_error_response()
    interest_country = session_attributes['country']
    full_report = session_attributes['full_report']
    speech_output = "Here is the travel warning for " + \
                        interest_country + '. Say stop at any time. ' + \
                        full_report + " What other country do you want travel warnings for?"
    reprompt_text = "Check on state department travel warnings by asking " \
                    "is england safe?"
    return build_response(session_attributes, build_speechlet_response(
    speech_output, reprompt_text, should_end_session))


def get_alert_details(intent, session):
    should_end_session = False
    session_attributes = {}
    speech_output = "Register your travel to receive alerts from the State Department. " +\
                    "Go to step.state.gov for more information. What country do you want travel warnings for?"
    reprompt_text = "What country do you want travel warnings for?"
    card_title = "What is STEP?"
    card_output = "The Smart Traveler Enrollment Program (STEP) " + \
                    "is a free service to allow U.S. citizens and nationals"+ \
                    " traveling abroad to enroll their trip with the nearest "+ \
                    "U.S. Embassy or Consulate. " + \
                    "Go to step.state.gov to register."
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session, card_title, card_output))

def get_embassy_details(intent, session):
    should_end_session = False
    session_attributes = {}
    speech_output = "If you have an emergency, contact the 24 Hour Consular line at " + \
                    "1-888-407-4747." + \
                    "You can find a full list of embassies at U.S. Embassy dot gov. What country do you want travel warnings for?"
    reprompt_text = "What country do you want travel warnings for?"
    card_title = "List of U.S. Embassies"
    card_output = "Go to usembassy.gov to find your embassy"
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session, card_title, card_output))

def restart(intent, session):
    should_end_session = False
    session_attributes = {}
    speech_output = "What other country do you want to know travel warnings for?"
    reprompt_text = "What country do you want travel warnings for?"
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session))

# --------------- Functions that call State Department API ------------------

def get_country_warning_from_rss(interest_country):
    request = urllib2.Request('https://travel.state.gov/_res/rss/TWs.xml')
    response = urllib2.urlopen(request)
    xml_string = response.read()
    interest_country_code = get_country_code(interest_country)

    xml_data = minidom.parseString(xml_string).getElementsByTagName('channel')
    countries = xml_data[0].getElementsByTagName('item')
    for country_data in countries:
        country_code_element = country_data.getElementsByTagName('dc:identifier')[0]
        country_code = country_code_element.childNodes[0].data.strip()
        if country_code == interest_country_code:
            publish_date = parse_date_string(country_data.getElementsByTagName('pubDate')[0].childNodes[0].data)
            html = country_data.getElementsByTagName('description')[0].childNodes[0].data.strip()
            index = html.find('<p>')
            summary = clean_html(html[:index])
            full_report = clean_html(html)
            return {"country": interest_country,
                        "publish_date": publish_date,
                        "summary": summary,
                        "full_report": full_report}
    return None

def parse_date_string(date_string):
    new_date_string = date_string[:-4]
    new_date = datetime.strptime(new_date_string,"%a, %d %b %Y %H:%M:%S")
    return new_date.strftime('%B %Y')

def get_country_code(country):
    new_country = check_alternatives(country)
    request = urllib2.Request('http://www.state.gov/developer/geoPoliticalArea.json')
    response = urllib2.urlopen(request)
    json_string = response.read()
    json_data = json.loads(json_string)
    for country_data in json_data:
        if new_country.lower() == country_data['Name'].lower():
            return country_data['Tag']
    return None

def check_alternatives(interest_country):
    country_alternatives = {
    "Antigua": "Antigua and Barbuda",
    "Ashmore": "Ashmore and Cartier Islands",
    "Bahamas": "Bahamas, The",
    "The Bahamas": "Bahamas, The",
    "Bosnia": "Bosnia and Herzegovina",
    "Congo": "Congo (Brazzaville)",
    "Falklands": "Falkland Islands (Islas Malvinas)",
    "Falkland Islands": "Falkland Islands (Islas Malvinas)",
    "Islas Malvinas": "Falkland Islands (Islas Malvinas)",
    "The Gambia": "Gambia, The",
    "Gambia": "Gambia, The",
    "North Korea": "Korea (Dem. Peoples Rep. of)",
    "Democratic Peoples Republic of Korea": "Korea (Dem. Peoples Rep. of)",
    "South Korea": "Korea (Republic of)",
    "Republic of Korea": "Korea (Republic of)",
    "Isle of Man": "Man, Isle of",
    "U.A.E.": "United Arab Emirates",
    "US": "United States",
    "America": "United States",
    "England": "United Kingdom",
    "U.K.": "United Kingdom",
    "Wales": "United Kingdom",
    "Scotland": "United Kingdom"
    }
    if interest_country in country_alternatives:
        return country_alternatives[interest_country]
    return interest_country

def clean_html(description):
    soup = BeautifulSoup(description)
    all_text = ' '.join(soup.findAll(text = True))
    for value in ['&#8211;', '&#8217;', '&#8220;', '&#8221;']:
        all_text = all_text.replace(value,'')
    return all_text.replace('&nbsp;',' ')


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SafetyIntent":
        return get_country_warning(intent, session)
    elif intent_name == "FullReportIntent":
        return get_full_report(intent, session)
    elif intent_name == "EmbassyIntent":
        return get_embassy_details(intent, session)
    elif intent_name == "AlertsIntent":
        return get_alert_details(intent, session)
    elif intent_name == "RestartIntent":
        return restart(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return get_error_response()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] !=
    #    raise ValueError("Invalid Application ID")
    #
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

countries = ['afghanistan', 'aland islands', 'albania', 'aleutian islands', 'algeria', 'american samoa', 'andaman islands', 'andorra', 'angola', 'anguilla', 'annobon', 'antarctica', 'antigua and barbuda', 'antipodes islands', 'argentina', 'armenia', 'aruba', 'ascension island', 'ashmore and cartier islands', 'auckland islands', 'australia', 'austria', 'azerbaijan', 'azores', 'bahamas, the', 'bahrain', 'baker island', 'balearic islands', 'bangladesh', 'barbados', 'bassas da india', 'belarus', 'belgium', 'belize', 'benin', 'bermuda', 'bhutan', 'bolivia', 'bosnia and herzegovina', 'botswana', 'bounty islands', 'bouvet island', 'brazil', 'british virgin islands', 'british indian ocean territory', 'brunei', 'bulgaria', 'burkina faso', 'burma', 'burundi', 'cambodia', 'cameroon', 'canada', 'canary islands', 'cape verde', 'cayman islands', 'central african republic', 'chad', 'chagos archipelago', 'chatham islands', 'chile', 'christmas island', 'clipperton island', 'cocos (keeling) islands', 'colombia', 'comoros', 'congo (brazzaville)', 'congo (kinshasa)', 'cook islands', 'coral sea islands', 'corsica', 'costa rica', "cote d'ivoire", 'crete', 'croatia', 'cuba', 'curacao', 'cyprus', 'czech republic', 'denmark', 'diego garcia', 'djibouti', 'dominica', 'dominican republic', 'ecuador', 'egypt', 'el salvador', 'equatorial guinea', 'eritrea', 'estonia', 'ethiopia', 'europa', 'falkland islands (islas malvinas)', 'faroe islands', 'fiji', 'finland', 'france', 'french guiana', 'french polynesia', 'french southern and antarctic lands', 'gabon', 'gambia, the', 'gaza strip', 'georgia', 'germany', 'ghana', 'gibraltar', 'glorioso islands', 'gough island', 'greece', 'greenland', 'grenada', 'guadeloupe', 'guam', 'guatemala', 'guernsey', 'guinea', 'guinea-bissau', 'guyana', 'haiti', 'heard island and mcdonald islands', 'honduras', 'hong kong', 'howland island', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy', 'jamaica', 'jan mayen', 'japan', 'jarvis island', 'jersey', 'johnston atoll', 'jordan', 'juan de nova island', 'kazakhstan', 'kenya', 'kermadec islands', 'kingman reef', 'kiribati', 'korea (dem. peoples rep. of)', 'korea (republic of)', 'kosovo', 'kuwait', 'kyrgyzstan', 'lakshadweep islands', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania', 'lord howe island', 'luxembourg', 'macau', 'macedonia', 'macquarie island', 'madagascar', 'madeira islands', 'malawi', 'malaysia', 'maldives', 'mali', 'mallorca', 'malta', 'man, isle of', 'marshall islands', 'martinique', 'mauritania', 'mauritius', 'mayotte', 'mexico', 'micronesia', 'midway islands', 'moldova', 'monaco', 'mongolia', 'montenegro', 'montserrat', 'morocco', 'mozambique', 'namibia', 'nauru', 'navassa island', 'nepal', 'netherlands', 'new caledonia', 'new zealand', 'nicaragua', 'nicobar islands', 'niger', 'nigeria', 'niue', 'norfolk island', 'northern mariana islands', 'norway', 'okinawa', 'oman', 'pakistan', 'palau', 'palmyra atoll', 'panama', 'papua new guinea', 'paracel islands', 'paraguay', 'peru', 'philippines', 'pitcairn islands', 'poland', 'portugal', 'puerto rico', 'qatar', 'reunion', 'romania', 'russia', 'rwanda', 'ryukyu islands', 'saint barthelemy', 'saint helena', 'saint kitts and nevis', 'saint lucia', 'saint martin', 'saint pierre and miquelon', 'saint vincent and the grenadines', 'samoa', 'san marino', 'sao tome and principe', 'saudi arabia', 'senegal', 'serbia and montenegro', 'seychelles', 'sierra leone', 'singapore', 'sint maarten', 'slovakia', 'slovenia', 'solomon islands', 'somalia', 'south africa', 'spain', 'spratly islands', 'sri lanka', 'south sudan', 'sudan', 'suriname', 'svalbard', 'swaziland', 'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'tasmania', 'thailand', 'timor-leste', 'togo', 'tokelau', 'tonga', 'trinidad and tobago', 'tristan da cunha', 'tromelin island', 'tunisia', 'turkey', 'turkmenistan', 'turks and caicos islands', 'tuvalu', 'uganda', 'ukraine', 'united arab emirates', 'united kingdom', 'united states', 'uruguay', 'us virgin islands', 'uzbekistan', 'vanuatu', 'vatican city (holy see)', 'venezuela', 'vietnam', 'wake island', 'wallis and futuna', 'west bank', 'western sahara', 'wrangel island', 'yemen', 'zambia', 'zimbabwe', 'antigua', 'ashmore', 'bahamas', 'the bahamas', 'bosnia', 'cocos islands', 'keeling islands', 'falkland islands', 'islas malvinas', 'the gambia', 'gambia', 'north korea', 'democratic peoples republic of korea', 'south korea', 'republic of korea', 'isle of man', 'sao tome', 'u.a.e.', 'u.s.', 'america', 'england', 'u.k.', 'wales', 'scotland', 'china']


