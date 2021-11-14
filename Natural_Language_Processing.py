import json
import requests
import spacy
from datetime import datetime
from bs4 import BeautifulSoup


# Function used to scrape a given BBC news article and return URL, Title, Date and Content as a json object
def bbc_scraper(url):
    # Error catching on invalid URL's and connectivity issues
    try:
        r = requests.session()
        page = r.get(url)
    except requests.exceptions.RequestException as e:
        print("Double check the URL and try again.")
        raise SystemExit(e)
    # Use beautifulSoup to parse the html content and store it as soup
    soup = BeautifulSoup(page.content, "html.parser")
    # Using beautifulSoup to find specific HTML tags within HTML classes
    title = soup.find("h1", id="main-heading").text
    full_date_tag = soup.find("time")
    if full_date_tag.has_attr('datetime'):
        # Scraping the datetime tag and stripping the final Z
        date_object = full_date_tag['datetime'].strip("Z")
        # Sets format of the date_object when scraped from the BBC website - example: 2020-04-11T19:01:56.000Z
        date_object = datetime.strptime(date_object,"%Y-%m-%dT%H:%M:%S.%f")
        # Use datetime module to reformat date tag into format dd MMM YYYY
        date_object = date_object.strftime("%d %B %Y")
    main_content = soup.findAll("div", class_="css-uf6wea-RichTextComponentWrapper e1xue1i82")
    paragraph_content = []
    # Loop through all the content stored in main_content
    for content in main_content:
        # Finds any lines in content which include CSS style tags
        for style in content("style"):
            # Removes the CSS style tags from the main_content - only necessary for Google colab - code passes test in Pycharm without this
            style.decompose()
    for elements in main_content:
        # Finding all "p" tags, this is used to remove any "li" tags that would be included otherwise
        if len(elements.findAll("p")) > 0:
            paragraph_content.append(elements.text)
            final_article = " ".join(paragraph_content)
        # Build the json object with content scraped from the website
    results_json = json.dumps({'URL': url, 'Title': title,'Date_published': date_object, 'Content': final_article})
    return results_json


# Function used to extract named entities from a string
def extract_entities(string):
    # Load the Spacy English model
    nlp = spacy.load("en_core_web_sm")
    # Pass the input string into Spacy to tokenize it
    string = nlp(string)
    people = []
    organisations = []
    places = []
    # Loop through each token(word) in the string and check what the word is
    for words in string.ents:
        # Finds any words that are organisations
        if words.label_ == "ORG":
            organisations.append(str(words))
        # Finds any words that are places
        elif words.label_ == "GPE":
            places.append(str(words))
        # Finds any words that are people
        elif words.label_ == "PERSON":
            people.append(str(words))
    # Build the json object with entities extracted from the in put string
    entities_json = json.dumps({'people': people, 'places': places, 'organisations': organisations})
    return entities_json


####################################################################
# Test cases

def test_bbc_scrape():
    results = {'URL': 'https://www.bbc.co.uk/news/uk-52255054',
                'Title': 'Coronavirus: \'We need Easter as much as ever,\' says the Queen',
                'Date_published': '11 April 2020',
                'Content': '"Coronavirus will not overcome us," the Queen has said, in an Easter message to the nation. While celebrations would be different for many this year, she said: "We need Easter as much as ever." Referencing the tradition of lighting candles to mark the occasion, she said: "As dark as death can be - particularly for those suffering with grief - light and life are greater." It comes as the number of coronavirus deaths in UK hospitals reached 9,875. Speaking from Windsor Castle, the Queen said many religions had festivals celebrating light overcoming darkness, which often featured the lighting of candles. She said: "They seem to speak to every culture, and appeal to people of all faiths, and of none. "They are lit on birthday cakes and to mark family anniversaries, when we gather happily around a source of light. It unites us." The monarch, who is head of the Church of England, said: "As darkness falls on the Saturday before Easter Day, many Christians would normally light candles together.  "In church, one light would pass to another, spreading slowly and then more rapidly as more candles are lit. It\'s a way of showing how the good news of Christ\'s resurrection has been passed on from the first Easter by every generation until now." As far as we know, this is the first time the Queen has released an Easter message. And coming as it does less than a week since the televised broadcast to the nation, it underlines the gravity of the situation as it is regarded by the monarch. It serves two purposes really; it is underlining the government\'s public safety message, acknowledging Easter will be difficult for us but by keeping apart we keep others safe, and the broader Christian message of hope and reassurance.  We know how important her Christian faith is, and coming on the eve of Easter Sunday, it is clearly a significant time for people of all faiths, but particularly Christian faith. She said the discovery of the risen Christ on the first Easter Day gave his followers new hope and fresh purpose, adding that we could all take heart from this.  Wishing everyone of all faiths and denominations a blessed Easter, she said: "May the living flame of the Easter hope be a steady guide as we face the future." The Queen, 93, recorded the audio message in the White Drawing Room at Windsor Castle, with one sound engineer in the next room.  The Palace described it as "Her Majesty\'s contribution to those who are celebrating Easter privately".  It follows a speech on Sunday, in which the monarch delivered a rallying message to the nation. In it, she said the UK "will succeed" in its fight against the coronavirus pandemic, thanked people for following government rules about staying at home and praised those "coming together to help others". She also thanked key workers, saying "every hour" of work "brings us closer to a return to more normal times".'}
    scraper_result = bbc_scraper('https://www.bbc.co.uk/news/uk-52255054')
    assert json.loads(scraper_result) == results


def test_extract_entities_amazon_org():
    input_string = "I work for Amazon."
    results_dict = {'people':[],
                    'places':[],
                    'organisations': ['Amazon']
                    }
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict


def test_extract_entities_name():
    input_string = "My name is Bob"
    results_dict = {'people':['Bob'],
                    'places':[],
                    'organisations': []
                    }
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict


test_bbc_scrape()
test_extract_entities_amazon_org()
test_extract_entities_name()