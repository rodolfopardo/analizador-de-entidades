from logging import log
import os
import json
import numpy as np


#import snowballstemmer
# import requests

# response = requests.get(url)
# response.raise_for_status()  # raises exception when not a 2xx response


from streamlit_lottie import st_lottie
from io import StringIO

import spacy
from spacy_streamlit import visualize_parser

import pandas as pd
import streamlit as st

import utils
import time
author_textrazor_token = os.getenv("TEXTRAZOR_TOKEN")
author_google_key = os.getenv("GOOGLE_KEY")
#print(author_google_key)

st.set_page_config(
    page_title="The Entities Swissknife",
    page_icon="https://cdn.shortpixel.ai/spai/q_lossy+ret_img+to_auto/https://studiomakoto.it/wp-content/uploads/2021/08/cropped-favicon-16x16-1-192x192.png",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None
    }
)

hide_st_style = """
            <style>
            footer {visibility: hidden;}
            [title^='streamlit_lottie.streamlit_lottie'] {
                margin-bottom: -35px;
                margin-top: -90px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# if "en_nlp" not in st.session_state:
#     st.session_state.en_nlp = spacy.load("en_core_web_sm")

# if "it_nlp" not in st.session_state:
#     st.session_state.it_nlp = spacy.load("it_core_news_sm")


# @st.cache(suppress_st_warning=True) 
# def logo():
# @st.cache(allow_output_mutation=True)
# def logo():


# # x= "anim"
# if  'anim'  not in st.session_state:
#     with open("data.json") as f:
#         st.session_state.anim = json.loads(f.read())

#     with st.sidebar:
#         st_lottie(st.session_state.anim, width=280, height=230, loop=False, key="anim_makoto")
# # # logo()

st.markdown(
        "###### [![this is an image link](https://studiomakoto.it/wp-content/uploads/2021/08/header-logo.webp)](https://studiomakoto.it/?utm_source=streamlit&utm_medium=app&utm_campaign=Entities-swissknife)"
    )

st.markdown(
        "###### Made in [![this is an image link](https://i.imgur.com/iIOA6kU.png)](https://www.streamlit.io/)&nbsp, with ❤️ by [@max_geraci](https://studiomakoto.it/makoto_member/massimiliano-geraci/) &nbsp | &nbsp [![Twitter Follow](https://img.shields.io/twitter/follow/max_geraci?style=social)](https://twitter.com/max_geraci) &nbsp | &nbsp [![this is an image link](https://i.imgur.com/thJhzOO.png)](https://www.buymeacoffee.com/MaxG.SEO)"
    )
@st.cache(allow_output_mutation=True)
def load_lottifile(filepath: str):
        with open(filepath, 'r') as f:
            return json.load(f)
loti_path = load_lottifile('data.json')
#st.title('Lotti')
with st.sidebar:
    
    #time.sleep(3)
    st_lottie(loti_path, width=280, height=180, loop=False)

df = None
texts=None  #initialize for 
language_option= None
#response2 = None
with st.form("my_form"):
    api_selectbox = st.sidebar.selectbox(
        "Choose the API you wish to use",
        ("TextRazor", "Google NLP")
    )
    input_type_selectbox = st.sidebar.selectbox(
        "Choose what you want to analyze",
        ("URL", "Text")
    )
    
    st.sidebar.info('##### Register on the [TextRazor website](https://www.textrazor.com/) to obtain a free API keyword (🙌 500 calls/day 🙌) or activate the [NLP API](https://cloud.google.com/natural-language) inside your Google Cloud Console, and export the JSON authentication file.') 
    st.sidebar.info('##### Knowledge Graph Entity ID is extracted only using the Google NLP API.') 
    st.sidebar.info('##### Categories and Topics - by [IPTC Media Topics](https://iptc.org/standards/media-topics/) - are avalaible only using the TextRazor API.') 
   
    # loti_path = load_lottifile('lotti/seo.json')
    # with st.sidebar:
    #     st_lottie(loti_path, width=280, height=130)
   
#st.title('Lotti')

    with st.expander("ℹ️ - About this app "):
        st.markdown(
            """  
            
This app, devoted to ✍️[Semantic Publishing](https://en.wikipedia.org/wiki/Semantic_publishing)✍️, relies on:
-   [Text Razor API](https://www.textrazor.com/) for Named-Entity Recognition ([NER](https://en.wikipedia.org/wiki/Named-entity_recognition)) and Linking ([NEL](https://en.wikipedia.org/wiki/Entity_linking));
-   [Google NLP API](https://cloud.google.com/natural-language) for NER and NEL;
-   Wikipedia API for scraping entities description;
-   [SpaCy for Streamlit](https://spacy.io/universe/project/spacy-streamlit) for Part-of-Speech Recognition
-   For everything else, the beauty and power of 🐍Python🐍 and Steamlit.
            
            """
        )
              
    with st.expander("✍️ - Semantic Publishing "):
        st.write(
            """  
            
The Entities Swissknife (TES) is a 100% 🐍Python🐍 app for Semantic publishing, i.e., publishing information on the web as documents accompanied by semantic markup (using the [schema.org](https://schema.org) vocabulary in JSON-LD format). Semantic publication provides a way for machines to understand the structure and meaning of the published information, making information search and data integration more efficient.
Semantic publishing relies on Structured Data adoption and Entity Linking (Wikification). Named entities are then injected into the JSON-LD markup to make the Content Topics explicit and 🥰Search engines friendly🥰: declare the main topic with the '[about](https://schema.org/about)' property and the secondary topics with the '[mentions](https://schema.org/mentions)' property).
The 'about' property should refer to 1-2 entities/topics at most, and these entities should be present in your H1 title. The 'mentions' properties should be no more than 3-5 depending on the article's length; as a general rule, an entities/topics should be explicitly mentioned in your schema markup if there is at least one paragraph dedicated to them (and they are possibly present in the relative headline).
The table with the "Top entities by Frequency" takes into account for the Frequency count also the normalized entities and not only the exact word with which the entities are present in the text.
            
            """
        )
        
    with st.expander("🔎 - How TES can support your Semantic SEO tasks "):
        st.write(
            """  
            
-   Know how NLU (Natural Language Understanding) algorithms “understand” your text to optimize it until the topics which are more relevant to you have the best relevance/salience score;
-   Analyze your SERP competitor’s main topics to discover possible topical gaps in your content;
-   Generate the JSON-LD markup (and inject it into your page schema) to explicit which topics your page is about to search engines. Declare your main topic with the 'about' property. Use the 'mentions' property to declare your secondary topics. This is helpful for disambiguation purposes too;
-   Analyze short texts such as a copy for an ad or a bio/description for an About-page (i.e., the [Entity Home](https://kalicube.com/faq/brand-serps/entity-home-in-seo-explainer/)).
-   Fine-tune the text until Google correctly recognizes the relevant entities and gives them desired salience. Use the SpaCy Part-of-Speech module to check how algorithms understand dependencies. Simplify the structure of the sentence if it is machines unfriendly.
           """
        )

    if api_selectbox == "TextRazor":
        google_api = None
        st.session_state.google_api = False
        if not author_textrazor_token:
            text_razor_key = st.text_input('Please enter a valid TextRazor API Key (Required)')
        else:
            text_razor_key = author_textrazor_token
    elif api_selectbox == "Google NLP":
        text_razor_key = None
        st.session_state.text_razor = False
        if not author_google_key:
            google_api = st.file_uploader("Please upload a valid Google NLP API Key (Required)", type=["json"])
            if google_api:
                google_api = json.loads(google_api.getvalue().decode("utf-8"))
        else:
            google_api = json.loads(author_google_key)
            #print(google_api)
        

    if input_type_selectbox == "URL":
        text_input = st.text_input('Please enter a URL', placeholder='https://gofishdigital.com/what-is-semantic-seo/')        
        #print('text_input 171 the first lien\n',text_input)
     
        meta_tags_only = st.checkbox('Extract Entities only from meta tags (tag_title, meta_description & H1-4)')
        #print('172 meta tag', meta_tags_only)
        if "last_field_type" in st.session_state and st.session_state.last_field_type != input_type_selectbox:
            st.session_state.text_razor = False
            st.session_state.google_api = False
        st.session_state.last_field_type = input_type_selectbox
    elif input_type_selectbox == "Text":
        
        if "last_field_type" not in st.session_state:
            st.session_state.last_field_type = input_type_selectbox
            st.session_state.text_razor = False
            st.session_state.google_api = False
        if st.session_state.last_field_type != input_type_selectbox:
            st.session_state.text_razor = False
            st.session_state.google_api = False
        st.session_state.last_field_type = input_type_selectbox
        meta_tags_only = False
        text_input = st.text_area('Please enter a text', placeholder='Posts involving Semantic SEO at Google include structured data, schema, and knowledge graphs, with SERPs that answer questions and rank entities - Bill Slawsky.')
    is_url = utils.is_url(text_input)
   # print('is_uri from 192 line\n', is_url)
    # spacy_pos = st.checkbox('Process Part-of-Speech analysis with SpaCy')
    spacy_pos = False
    scrape_all = st.checkbox("Scrape ALL the Entities descriptions from Wikipedia. This is a time-consuming task, so grab a coffee if you need all the descriptions in your CSV file. The descriptions of the Entities you select for your 'about' and 'mentions' schema properties will be scraped and present in the corresponding JSON-LD files")
    #rint('Scrape all', scrape_all)
    if api_selectbox == "TextRazor":
        extract_categories_topics = st.checkbox('Extract Categories and Topics')
    submitted = st.form_submit_button("Submit")
    if submitted:
#         loti_path = load_lottifile('lotti/seo2.json')
# #st.titl
#         st_lottie(loti_path, width=280, height=130, loop=True)

        if not text_razor_key and not google_api:
            st.warning("Please fill out all the required fields")
        elif not text_input:
            st.warning("Please Enter a URL/Text in the required field")
        else:
            st.session_state.submit = True
            if api_selectbox == "TextRazor":
                output, response, topics_output, categories_output = utils.get_df_text_razor(text_razor_key, text_input, extract_categories_topics, is_url, scrape_all)
                #print('output 167 line:\n', output) #-------------------------
               # print('response 213 line :\n',response)
                st.session_state.text = response.cleaned_text
                #response1 = [response.cleaned_text]
                #----------------------updated--------------
                texts = st.session_state.text
                #--------------------end--------------------
                #print('response.cleaned_text\n', response.cleaned_text)
                #-------------------------------------------------------------------
                st.session_state.text_razor = True
                st.session_state.df_razor = pd.DataFrame(output)
                if topics_output:
                    st.session_state.df_razor_topics = pd.DataFrame(topics_output)
                if categories_output:
                    st.session_state.df_razor_categories = pd.DataFrame(categories_output)
            elif api_selectbox == "Google NLP":
                output, response = utils.get_df_google_nlp(google_api, text_input, is_url, scrape_all)
                #print('is_url', is_url)
                #response1 = list(response)
                response1 = [response]
                response2 = list(response1)
                #response2 = response2[0].lower()
                #print('type of response \n', type(response))
                #print()
                # st.write('response==>\n', response)
                # st.write('response==>\n', response2)
                #st.write('is_arul\n', is_url)
                #st.write('233 response.clean.txt', response.cleaned_text)
                #texts = response
                #print('229 line response google api', response)
                #print('201 text output', output)
                # print('response', response.clean)
                st.session_state.text = text_input  #just gives the url for google api text_intput from url
                #print("text_input 233 output google api", text_input)
                st.session_state.google_api = True
                st.session_state.df_google = pd.DataFrame(output)
            
            st.session_state.lang = response.language
            language_option = response.language
           # print('langu form==>', response.language)
#---------------------------------------------Frequency Counter------------------
#
# @st.cache
def word_frequency(df, text_input, language_option, texts= texts):

        from nltk.stem.snowball import SnowballStemmer

        if language_option == 'eng':

            stemmer = SnowballStemmer(language='english')
        else:

            stemmer = SnowballStemmer(language='italian')

        #stemmer = snowballstemmer.stemmer('english')
        #if len(texts) >0 :
        if texts==None:
            #text_input = texts
            text_input= text_input
        else:
            text_input=texts
        tokens = text_input.split()
        stem_words = []
        for token in tokens:
            stem_words.append(stemmer.stem(token))
            #stem_words.append(stemmer.stemWords(token))
           
        word_count = []
        txt = text_input.lower()
        for word in list(df['name']):
            word = word.lower()
            stem_word = stemmer.stem(word)
            #stem_word = stemmer.stemWords(word)
            count = txt.count(word)
            if count == 0 :
                
                count = stem_words.count(stem_word)
                word_count.append(count)
                continue
           

            word_count.append(count)
        df = df.insert(loc=3, column='Frequency', value=np.array(word_count)) 
        return df
#-------------------------------------------end----------------------------------------------
# #----------------------------Convert Confidence score value into percentage----------------------
# def conf(col):
#     if col in df:
#         df[col] = (df[[col]].div(max(df[col]), axis=1)*100).round(2).astype(str) + '%'
 
#  #-------------------------------------end----------------------------------------------



if 'submit' in st.session_state and ("text_razor" in st.session_state and st.session_state.text_razor == True):
    text_input, is_url = utils.write_meta(text_input, meta_tags_only, is_url)
   # print('text_input\n', text_input)
   # print('is_url\n', is_url)
    if 'df_razor' in st.session_state:
        df = st.session_state["df_razor"]

    if len(df) > 0:
        df['temp'] = df['Relevance Score'].str.strip('%').astype(float)
        df = df.sort_values('temp', ascending=False)
        del df['temp']
        selected_about_names = st.multiselect('Select About Entities:', df.name)
        selected_mention_names = st.multiselect('Select Mentions Entities:', df.name)
        #--------------Frequency count--------------
    #if not url:
    word_frequency(df, text_input, language_option, texts) #-----------------------Function call for textrazor-------------
    #print(is_url)
    #print(text_input)
    utils.conf(df, "Confidence Score")
    st.write('### Entities', df)
    #st.write('#### Entity table Dimension', df.shape)
    df1 = df.sort_values('Frequency', ascending=False)
    st.write('### Top 10 Entities by Frequency', df1[['name', 'Frequency']].head(10))
    #st.write(response1)

    c, t = st.columns(2)
    if 'df_razor_categories' in st.session_state and extract_categories_topics:
        with c:
            df_categories = st.session_state["df_razor_categories"]
            st.write('### Categories', df_categories)
    if 'df_razor_topics' in st.session_state and extract_categories_topics:
        with t:
            df_topics = st.session_state["df_razor_topics"]
            st.write('### Topics', df_topics)
    
    if len(df) > 0:
        about_download_button = utils.download_button(utils.convert_schema("about", df.loc[df['name'].isin(selected_about_names)].to_json(orient='records'), scrape_all, st.session_state.lang), 'about-entities.json', 'Download About Entities JSON-LD ✨', pickle_it=False)
        if len(df.loc[df['name'].isin(selected_about_names)]) > 0:
            st.markdown(about_download_button, unsafe_allow_html=True)
        mention_download_button = utils.download_button(utils.convert_schema("mentions", df.loc[df['name'].isin(selected_mention_names)].to_json(orient='records'), scrape_all, st.session_state.lang), 'mentions-entities.json', 'Download Mentions Entities JSON-LD ✨', pickle_it=False)
        if len(df.loc[df['name'].isin(selected_mention_names)]) > 0:
            st.markdown(mention_download_button, unsafe_allow_html=True)
    if "df_razor_topics" in st.session_state and extract_categories_topics:
        df_topics = st.session_state["df_razor_topics"]
        download_buttons = ""
        download_buttons += utils.download_button(df_topics, 'topics.csv', 'Download all Topics CSV ✨', pickle_it=False)
        st.markdown(download_buttons, unsafe_allow_html=True)
    if "df_razor_categories" in st.session_state and extract_categories_topics:
        df_categories = st.session_state["df_razor_categories"]
        download_buttons = ""
        download_buttons += utils.download_button(df_categories, 'categories.csv', 'Download all Categories CSV ✨', pickle_it=False)
        st.markdown(download_buttons, unsafe_allow_html=True)
    if len(df) > 0:
        download_buttons = ""
        download_buttons += utils.download_button(df, 'entities.csv', 'Download all Entities CSV ✨', pickle_it=False)
        st.markdown(download_buttons, unsafe_allow_html=True)
    if spacy_pos:
        if st.session_state.lang in "eng":
            #print('textrazor-eng lang\n', st.session_state.lang)
            doc = st.session_state.en_nlp(st.session_state.text)
        elif st.session_state.lang in "ita":
            #print('textrazor-ita lang\n', st.session_state.lang)
            doc = st.session_state.it_nlp(st.session_state.text)
        visualize_parser(doc)
#---------------------google api frequency count-----------------
# def word_frequency1(df, response2):
    
#         import math
#         word_count = []
        
#         for word in list(df['name']):
#             word = word.lower()
           
#             count = response2.count(word)/2
#             count= math.ceil(count)
#             print('inside funtion response1\n')
#             word_count.append(count)
            
#         df = df.insert(loc=3, column='Frequency', value=np.array(word_count))
#        # df['Frequency2'] = df['Frequency2'].astype('int64')
#         return df
if 'submit' in st.session_state and ("google_api" in st.session_state and st.session_state.google_api == True):
    text_input, is_url = utils.write_meta(text_input, meta_tags_only, is_url)
    # st.write('text_input 380|', text_input)
    # st.write('is url 380\n', is_url)
    if 'df_google' in st.session_state:
        df = st.session_state["df_google"]
    if len(df) > 0:
        df['temp'] = df['Salience'].str.strip('%').astype(float)
        df = df.sort_values('temp', ascending=False)
        del df['temp']
        selected_about_names = st.multiselect('Select About Entities:', df.name)
        selected_mention_names = st.multiselect('Select Mentions Entities:', df.name)
        #---------------------frequency counter
    #response1 = [response]
    utils.conf(df, "Confidence Score")
    st.write('### Entities', df)
    # if not is_url:
    #     word_frequency(df, text_input, language_option, texts) 
    # # else:
    # #     word_frequency1(df,  response2)        #-----------------function call for google api
    # st.write('### Entities', df)
    
    # st.write('#### Entity table Dimension', df.shape)
    # if not is_url:
    #     df1 = df.sort_values('Frequency', ascending=False)
    #     st.write('### Top 10 Entities', df1[['name', 'Frequency']].head(10))
    
    #response2 = list(response)
    #st.write(response1)
    #st.write(response2)
    #st.write(type(response1))
    #st.write(type(response2))
    
    if len(df) > 0:
        about_download_button = utils.download_button(utils.convert_schema("about", df.loc[df['name'].isin(selected_about_names)].to_json(orient='records'), scrape_all, st.session_state.lang), 'about-entities.json', 'Download About Entities JSON-LD ✨', pickle_it=False)
        if len(df.loc[df['name'].isin(selected_about_names)]) > 0:
            st.markdown(about_download_button, unsafe_allow_html=True)
        mention_download_button = utils.download_button(utils.convert_schema("mentions", df.loc[df['name'].isin(selected_mention_names)].to_json(orient='records'), scrape_all, st.session_state.lang), 'mentions-entities.json', 'Download Mentions Entities JSON-LD ✨', pickle_it=False)
        if len(df.loc[df['name'].isin(selected_mention_names)]) > 0:
            st.markdown(mention_download_button, unsafe_allow_html=True)
        download_buttons = ""
        download_buttons += utils.download_button(df, 'entities.csv', 'Download all Entities CSV ✨', pickle_it=False)
        st.markdown(download_buttons, unsafe_allow_html=True)
    if spacy_pos:
        if st.session_state.lang in "eng":
            doc = st.session_state.en_nlp(st.session_state.text)
            #print('English', doc)
        elif st.session_state.lang in "ita":
            doc = st.session_state.it_nlp(st.session_state.text)
            #print('Itelian')
        visualize_parser(doc)
