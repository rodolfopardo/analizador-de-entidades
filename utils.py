import base64
import os
import json
import pickle
import uuid
import re
import simplejson
import unidecode

import wikipediaapi
from textrazor import TextRazorAnalysisException
from analyzer import TextRazorAnalyzer, GoogleNLPAnalyzer
import validators
import extruct
from bs4 import BeautifulSoup
from w3lib.html import get_base_url
from dateutil import parser
import streamlit as st
import pandas as pd
import requests

en_wiki_wiki = wikipediaapi.Wikipedia('en')
it_wiki_wiki = wikipediaapi.Wikipedia('it')


google_types = {
    0 :"UNKNOWN",
    1 :"PERSON",
    2 :"LOCATION",
    3 :"ORGANIZATION",
    4 :"EVENT",
    5 :"WORK_OF_ART",
    6 :"CONSUMER_GOOD",
    7 :"OTHER",
    9 :"PHONE_NUMBER",
    10 :"ADDRESS",
    11 :"DATE",
    12 :"NUMBER",
    13 :"PRICE",
}


def get_summary_link(title, lang):
    """Get summary from Wikipedia.

    Args:
        title (str): the title of the article.
        lang (str): the language of the article.

    Returns:
        str: the summary of the article.
        str: the link of the article.
    """
    try:
        if lang in "ita":
            wiki_wiki = it_wiki_wiki
        else:
            wiki_wiki = en_wiki_wiki
        
        page = wiki_wiki.page(title)

        summary = page.summary
        summary = ". ".join(summary.split(".")[:2])
        summary = summary.replace("\n", " ").replace(",", " ").replace("  ", " ")
        summary = unidecode.unidecode(summary)

        if lang in "ita":
            try:
                en_link = page.langlinks["en"].fullurl
                it_link = page.fullurl
            except:
                en_link = ""
                it_link = page.fullurl
        else:
            en_link = page.fullurl
            try:
                it_link = page.langlinks["it"].fullurl
            except:
                it_link = ""
        return summary, en_link, it_link
    except Exception as e:
        print(e)
        return None, None, None


def convert_schema(schema_type, data, scrape_all, lang):
    """Convert the dataframe to the schema.

    Args:
        schema_type (str): name of the schema, can be (about, mentions).
        data (str): the data to be converted.
        scrape_all (boolean): if True, all the data will be scraped.
        lang (str): the language of the data.

    Returns:
        str: the converted data.
    """
    header = '<script type="application/ld+json">\n'
    footer = "\n</script>"
    data = json.loads(data)
    result = []
    for d in data:
        item = {}
        
        item["@context"] = "http://schema.org"
        item["@type"] = "Thing"
        item["name"] = d["name"]
        if not scrape_all:
            item["description"] = get_summary_link(d["name"], lang)[0]
        
        if "Wikidata Id" in d and "Wikipedia Link" in d:
            item["SameAs"] = [
                d.pop("Wikipedia Link", None),
                "https://www.wikidata.org/wiki/" + d.pop("Wikidata Id", None)
            ]
        elif "Wikipedia Link" in d:
            item["SameAs"] = [
                d.pop("Wikipedia Link", None)
            ]
        result.append(item)
    return header + json.dumps([{f"{schema_type}": result}], indent=4 * ' ') + footer


def extract_tags_text(url):
    """Extract the tags from the url.
    
    Args:
        url (str): the url of the page.
    
    Returns:
        title (str): the title of the page.
        desc (str): the description of the page.
        h1_list (str): the list of h1 tags.
        h2_list (str): the list of h2 tags.
        h3_list (str): the list of h3 tags.
    """
    headers = {'User-Agent': 'My User Agent 1.0'}
    html_content = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_content, "lxml")
    title = soup.title.text
    desc = soup.find("meta", attrs={"name": "description"})
    if desc:
        desc = desc.get("content", "")
    h1_list = """\n\n""".join([" " + str(tag.text) for tag in soup.select("h1")])
    h2_list = """\n\n""".join([" " + str(tag.text) for tag in soup.select("h2")])
    h3_list = """\n\n""".join([" " + str(tag.text) for tag in soup.select("h3")])
    return title, desc, h1_list, h2_list, h3_list



def is_url(text):
    """Check if a string is a valid URL.
    
    """
    if validators.url(text.strip()):
        return True
    else:
        return False


def is_time(text):
    """Check if a string is a valid time.
    """
    try:
        parser.parse(text)
        return True
    except Exception:
        return False


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.

    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.

    Returns:
    -------
    (str): the anchor tag to download object_to_download

    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')

    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        elif isinstance(object_to_download, str):
            pass
        else:
            object_to_download = simplejson.dumps(json.loads(object_to_download), indent=4 * ' ')

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()
    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                border-color: rgb(246, 51, 102);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1.5px;
                border-style: solid;
                border-image: initial;

            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


def get_html(url):
    """Get raw HTML from a URL."""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers=headers)
    return req.text


def scrape(url):
    """Parse structured data from a target page."""
    html = get_html(url)
    metadata = get_metadata(html, url)
    return json.dumps(metadata, indent=4)


def get_metadata(html, url):
    """Fetch JSON-LD structured data."""
    metadata = extruct.extract(
        html,
        base_url=get_base_url(html, url),
        syntaxes=['json-ld'],
    )['json-ld']
    if bool(metadata) and isinstance(metadata, list):
        metadata = metadata[0]
    return metadata


def get_df_text_razor(text_razor_key, text_input, extract_categories_topics, is_url, scrape_all):
    #x = True
    """ Get data using TextRazor API.

    Args:
        text_razor_key (str): TextRazor API key.
        text_input (str): Text to analyze.
        extract_categories_topics (boolean): If True, extract categories and topics.
        is_url (bool): If True, text_input is a URL.
        scrape_all (boolean): If True, scrape all data.

    Returns:
        output (list): List of dictionaries containing extracted data.
        response (TextRazorResponse): TextRazor response object.
        topics_output (list): List of dictionaries containing extracted topics.
        categories_output (list): List of dictionaries containing extracted categories.
    """
    progress_val = 0
    progress_bar = st.progress(progress_val)
    try:
        analyzer = TextRazorAnalyzer(text_razor_key)
        response = analyzer.analyze(text_input, is_url)
    except TextRazorAnalysisException:
        st.warning("Please make sure that the API Key is correct")
        st.stop()
    
    output = []
    known_entities = []
    for i, entity in enumerate(response.entities()):
        progress_val += 1
        if entity.id not in known_entities and\
        entity.confidence_score > 0 and\
        entity.relevance_score > 0 and\
        not str(entity.id).isnumeric() and not is_time(entity.id):
            summary = ""
            en_link = ""
            if scrape_all:# or x:
                summary, en_link, it_link = get_summary_link(entity.id, response.language)
            if entity.dbpedia_types:
                entity_type = entity.dbpedia_types[0]
            elif entity.freebase_types:
                entity_type = entity.freebase_types[0]
            else:
                entity_type = "thing"
            data = {
                "DBpedia Category": entity_type.split("/")[-1],
                "name": entity.id,
                "description": summary,
                "Wikidata Id": entity.wikidata_id,
                "Confidence Score": entity.confidence_score,
                #"Confidence Score":f"{(entity.confidence_score/max(entity.confidence_score))* 100:.2f}%",
                "Relevance Score": f"{entity.relevance_score * 100:.2f}%",
                "Wikipedia Link": entity.wikipedia_link,
                "English Wikipedia Link": en_link,
            }
            if not scrape_all:
                del data["description"]
                del data["English Wikipedia Link"]
            output.append(data)
            known_entities.append(entity.id)
        progress_bar.progress((progress_val)/len(response.entities()))
    topics_output = []
    categories_output = []
    if extract_categories_topics:
        for i, topic in enumerate(response.topics()):
            topics_output.append(
                {
                    "label": topic.label,
                    "score": topic.score
                }
            )
        for i, category in enumerate(response.categories()):
            categories_output.append(
                {
                    "label": category.label.split(">")[-1],
                    "score": category.score
                }
            )
    return output, response, topics_output, categories_output

#----------------------------Convert Confidence score value into percentage----------------------
def conf(df, col):
    if col in df:
        df[col] = (df[[col]].div(max(df[col]), axis=1)*100).round(2).astype(str) + '%'
 
 #-------------------------------------end----------------------------------------------


def get_df_google_nlp(key, text_input, is_url, scrape_all):
    #x = True
   # scrape_all= True
    """ Get data using Google Natural Language API.

    Args:
        key (str): Google Natural Language API key.
        text_input (str): Text to analyze.
        is_url (boolean): If True, text_input is a URL.
        scrape_all (boolean): If True, scrape all data.

    Returns:
        output (list): List of dictionaries containing extracted data.
        response (GoogleNLPResponse): Google Natural Language API response object.
    """
    progress_val = 0
    progress_bar = st.progress(progress_val)
    try:
        analyzer = GoogleNLPAnalyzer(key)
        response = analyzer.analyze(text_input, is_url)
        if not response:
            st.warning("Please make sure that the API Key is correct")
            st.stop()
    except Exception as e:
        print(e)
        st.warning("Please make sure that the API Key is correct")
        st.stop()
    
    output = []
    known_entities = []
    for i, entity in enumerate(response.entities):
        progress_val += 1
        if entity.name not in known_entities and\
        not str(entity.name).isnumeric() and not is_time(entity.name):
            summary = ""
            en_link = ""
            it_link = ""
            if scrape_all:#or x:
                summary, en_link, it_link = get_summary_link(entity.name, response.language)
                lang = response.language

            if entity.metadata.get("mid"):
                mid = "https://www.google.com/search?kgmid=" + entity.metadata.get("mid")
            else:
                mid = ""
            if entity.type_:
                row_type = google_types[entity.type_]
                if row_type in ["NUMBER", "PRICE", "DATE"]:
                    continue
            else:
                row_type = "thing"
            data = {
                "type": row_type,
                "name": unidecode.unidecode(entity.name),
                "description": summary,
                "Salience": f"{entity.salience * 100:.2f}%",
                "Knowledge Graph ID": mid,
                "Italian Wikipedia Link": it_link,
                "English Wikipedia Link": en_link,
            }
            #print('\nLanguage\n', response.language)
            if not scrape_all:
                del data["description"]
                del data["English Wikipedia Link"]
                del data["Italian Wikipedia Link"]
            # if not scrape_all and lang == "it":
            #     del data["English Wikipedia Link"]
            # if  lang == "en":
            #     del data["Italian Wikipedia Link"]
            output.append(data)
            known_entities.append(entity.name)
        progress_bar.progress((progress_val)/len(response.entities))
    return output, response

def write_meta(text_input, meta_tags_only, is_url):
    """ Concatenate meta tags with input text.

    Args:
        text_input (str): Text to analyze.
        meta_tags_only (boolean): If True, write only meta tags.
        is_url (boolean): If True, text_input is a URL.
    """
    if meta_tags_only and is_url:
        meta_title, meta_description, h1, h2, h3 = extract_tags_text(text_input)
        if meta_title:
            st.write('### Meta Title')
            st.info(meta_title)
        if meta_description:
            st.write('### Meta Description')
            st.info(meta_description)
        if h1:
            st.write('### H1')
            st.info(h1)
        if h2:
            st.write('### H2')
            st.info(h2)
        if h3:
            st.write('### H3')
            st.info(h3)
        meta_input = [meta_title, meta_description, h1, h2, h3]
        text_input = " ".join([m for m in meta_input if m])
        is_url = False
        return text_input, is_url
    else:
        return text_input, False
