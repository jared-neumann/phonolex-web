from re import S
import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image

img = Image.open("images/phonolex-icon.png")

st.set_page_config(
    page_title="PhonoLex",
    page_icon=img,
    layout="wide"
    )

if 'ptrn_phonemes' not in st.session_state:
    st.session_state.ptrn_phonemes = []

@st.cache
def load_data(source = 'common_lemmas'):

    sources = ['common_lemmas', 'common_words', 'all_words']

    if source not in sources:
      raise ValueError("Invalid source. Expected one of %s" % sources)

    if source == 'common_lemmas':
      return pd.read_pickle('data/common_lemmas.pkl')
    elif source == 'common_words':
      return pd.read_pickle('data/common_words.pkl')
    elif source == 'all_words':
      return pd.read_pickle('data/all_words.pkl')

def word_level_filter(df, diphthongs = False, characters = (1,20), phonemes = (1,20), syllables = (1,10)):

    filtered_data = df[
            (df.character_length.astype(int) >= characters[0]) & (df.character_length.astype(int) <= characters[1])
            & (df.phoneme_length.astype(int) >= phonemes[0]) & (df.phoneme_length.astype(int) <= phonemes[1])
            & (df.syllables.astype(int) >= syllables[0]) & (df.syllables.astype(int) <= syllables[1])
        ]
    
    if diphthongs == False:
        filtered_data = filtered_data[
            (filtered_data.contains_diphthong.astype(bool) == False)
        ]

    return filtered_data

def compare_phonemes(word_phonemes, ptrn_phonemes):

    match = True

    if len(ptrn_phonemes) <= len(word_phonemes):
            for i in range(0, len(ptrn_phonemes)):
                
                ptrn_phoneme = ptrn_phonemes[i]
                word_phoneme = word_phonemes[i]

                if len(ptrn_phoneme) == 0:
                    continue

                for feature in ptrn_phoneme:

                    if ptrn_phoneme[feature] != None:
                        
                        if feature == 'TYPE':
                            if ptrn_phoneme[feature] in word_phoneme[feature]:
                                continue
                            else:
                                match = False
                                break
                    
                        else:
                            
                            p = set(ptrn_phoneme[feature])
                            w = set(word_phoneme[feature])

                            if len(w.intersection(p)) > 0:
                                continue
                            else:
                                match = False
                                break

                    else:
                        continue
    else:
        match = False
    
    return match

def begins_with_pattern(df, ptrn_phonemes):

    valid_rows = []

    for index, row in df.iterrows():
        
        word_phonemes = row['features']
        
        match = compare_phonemes(word_phonemes, ptrn_phonemes)

        if match == True:
            valid_rows.append(row)
    
    return pd.DataFrame(valid_rows)

def ends_with_pattern(df, ptrn_phonemes):

    valid_rows = []

    for index, row in df.iterrows():

        word_phonemes = row['features']

        reverse_word = word_phonemes[::-1]
        reverse_ptrn = ptrn_phonemes[::-1]

        match = compare_phonemes(reverse_word, reverse_ptrn)

        if match == True:
            valid_rows.append(row)
    
    return pd.DataFrame(valid_rows)

def exactly_matches_pattern(df, ptrn_phonemes):

    valid_rows = []

    for index, row, in df.iterrows():

        word_phonemes = row['features']

        match = True

        if len(ptrn_phonemes) == len(word_phonemes):
                for i in range(0, len(ptrn_phonemes)):
                    ptrn_phoneme = ptrn_phonemes[i]
                    word_phoneme = word_phonemes[i]
                    if len(ptrn_phoneme) == 0:
                        continue
                    for feature in ptrn_phoneme:
                        if ptrn_phoneme[feature] != None:   
                            if feature == 'TYPE':
                                if ptrn_phoneme[feature] in word_phoneme[feature]:
                                    continue
                                else:
                                    match = False
                                    break
                            else:  
                                p = set(ptrn_phoneme[feature])
                                w = set(word_phoneme[feature])
                                if len(w.intersection(p)) > 0:
                                    continue
                                else:
                                    match = False
                                    break
                        else:
                            continue
        else:
            match = False
        
        if match == True:
            valid_rows.append(row)

    return pd.DataFrame(valid_rows)

def contains_pattern(df, ptrn_phonemes):
    
    valid_rows = []

    for index, row, in df.iterrows():

        word_phonemes = row['features']

        match = False

        while match == False and len(word_phonemes) >= len(ptrn_phonemes):

            if compare_phonemes(word_phonemes, ptrn_phonemes) == False:
                word_phonemes.pop(0)
                continue
            else:
                valid_rows.append(row)
                match = True
    
    return pd.DataFrame(valid_rows)

with st.sidebar:
    st.header('About')
    st.markdown(
        """
        <b>PhonoLex</b> is an application that allows you to 
        find words given a set of word-level features 
        and phonetic patterns.
        """,
        unsafe_allow_html=True
    )
    
    st.header('Word Lists')
    st.markdown(
        """
        Given criteria are checked against a word list. 
        There are three options: <i>common lemmas</i>, <i>common
        words</i>, and <i>all words</i>.

        <i>all words</i>: derived from the
        <a href="http://www.speech.cs.cmu.edu/cgi-bin/cmudict">CMU Pronouncing Dictionary</a>.
        Proper nouns and non-English words removed.

        <i>common words</i>: derived from the top 5000 lemmas and word forms in the 
        <a href="https://www.wordfrequency.info/samples.asp">COCA 2020 Word Frequency Data</a>.
        Cross-referenced with the CMU Pronouncing Dictionary.

        <i>common lemmas</i>: derived from the top 5000 lemmas in the 
        COCA Word Frequency Data linked above.
        Cross-referenced with the CMU Pronouncing Dictionary.
        """,
        unsafe_allow_html=True
    )

    st.header('Word-Level Features')
    st.markdown(
        """
        Optional set of four word-level features that are adjustable.
        Limit the results by setting minimum and maximum numbers
        of characters, phonemes, and syllables, and select whether
        to allow diphthongs.

        Submit the form before searching.
        """,
        unsafe_allow_html=True
    )

    st.header('Phoneme-Level Features')
    st.markdown(
        """
        Define phonemes using their features. First, select whether
        the phoneme you are defining is a consonant or vowel. The relevant
        features will then appear. Add any number of these features. The app
        will search for results containing all <i>types</i> of features
        defined, e.g., VOICE, MANNER, <b>and</b> PLACE, and containing any of the
        features defined within each, e.g., 'fricative' <b>or</b> 'affricate'.

        Empty features match anything.
        """,
        unsafe_allow_html=True
    )

    st.header('Pattern Building')
    st.markdown(
        """
        Build a pattern of phonemes defined above by adding them in the 
        desired order. Currently, there is no way to re-order or delete
        phonemes. To start over, you will have to refresh the page.
        
        Select the pattern-matching mode, which determines where in a word
        the pattern should appear. Note: empty phonemes are allowed, and match anything.
        """,
        unsafe_allow_html=True
    )

    st.markdown('---')
    st.markdown(
        """
        <p>Author: Jared Neumann</p>
        <p>Github: <a href="https://github.com/jared-neumann">jared-neumann</a></p>  
        <p>Version: 1.0.0</p>
        <p>Copyright 2022</p>
        """,
        unsafe_allow_html=True
        )

        
st.markdown("<h1 style='text-align: left; color: black;'>PhonoLex</h1>", unsafe_allow_html=True)

with st.expander('Word List Selection (Default: common lemmas)'):
    data_option = st.selectbox('', ['common lemmas', 'common words', 'all words'])

st.markdown('---')

with st.expander('Word-Level Features (Default: allow everything except diphthongs)'):
    with st.form(key = 'word_features'):

        col_diphthong, col_characters, empty1, col_phonemes, empty2, col_syllables = st.columns([1.35,1,0.33,1,0.33,1])
        with col_diphthong:
            st.markdown('')
            st.markdown('')
            contains_diphthong = st.checkbox("allow diphthongs")
        with col_characters:
            character_length = st.slider("# of characters:", min_value = 1, max_value = 20, value = (1, 20), step = 1)
        with col_phonemes:
            phoneme_length = st.slider("# of phonemes:", min_value = 1, max_value = 20, value = (1, 20), step = 1)
        with col_syllables:
            syllables = st.slider("# of syllables:", min_value = 1, max_value = 10, value = (1, 10), step = 1)

        submit = st.form_submit_button(label='Submit')


st.markdown('---')

with st.expander('Phoneme Features and Pattern-Building (Default: none)'):
    col_mode, empty_0, empty_1 = st.columns(3)
    with col_mode:
        mode_option = st.selectbox('PATTER-MATCHING MODE', ['begins with', 'ends with', 'contains', 'exactly matches'])
    col_type, empty_2, empty_3 = st.columns(3)
    with col_type:
        type = st.selectbox('TYPE', ['', 'consonant', 'vowel'])
    with st.form(key='ptrn_phoneme'):

        voice = None
        manner = None
        place = None
        shape = None
        height = None
        depth = None

        if type == 'consonant':
            col_voice, col_manner, col_place = st.columns(3)
            
            with col_voice:
                voice = st.selectbox('VOICE', ['', 'voiced', 'unvoiced'])
            with col_manner:
                manner = st.multiselect('MANNER', ['stop', 'affricate', 'fricative', 'liquid', 'glide', 'lateral', 'rhotic', 'nasal'])
            with col_place:
                place = st.multiselect('PLACE', ['bilabial', 'labiodental', 'dental', 'labiovelar', 'alveolar', 'postalveolar', 'alveopalatal', 'palatal', 'velar', 'glottal'])

        if type == 'vowel':
            col_shape, col_height, col_depth = st.columns(3)

            with col_shape:
                shape = st.selectbox('SHAPE', ['', 'rounded', 'unrounded'])
            with col_height:
                height = st.multiselect('HEIGHT', ['open', 'near-open', 'open-mid', 'mid', 'close-mid', 'near-close', 'close'])
            with col_depth:
                   depth = st.multiselect('DEPTH', ['front', 'near-front', 'central', 'near-back', 'back'])

        add_phoneme = st.form_submit_button(label='Add')

if add_phoneme:
    ptrn_phoneme = {
        'TYPE': None,
        'VOICE': None,
        'MANNER': None,
        'PLACE': None,
        'SHAPE': None,
        'HEIGHT': None,
        'DEPTH': None
    }
    if type != None and type != '':
        ptrn_phoneme['TYPE'] = type
    if voice != None and voice != '':
        ptrn_phoneme['VOICE'] = [voice]
    if manner != None and len(manner) > 0 and manner != '':
        ptrn_phoneme['MANNER'] = manner
    if place != None and len(place) > 0 and place != '':
        ptrn_phoneme['PLACE'] = place
    if shape != None and shape != '':
        ptrn_phoneme['SHAPE'] = [shape]
    if height != None and len(height) > 0 and height != '':
        ptrn_phoneme['HEIGHT'] = height
    if depth != None and len(depth) > 0 and depth != '':
        ptrn_phoneme['DEPTH'] = depth
    st.session_state.ptrn_phonemes.append(ptrn_phoneme)

if len(st.session_state.ptrn_phonemes) > 0:
    st.markdown('---')
    st.markdown("<h5 style='text-align: left; color: black;'>Pattern</h5>", unsafe_allow_html=True)

    ptrn = pd.DataFrame(st.session_state.ptrn_phonemes)
    ptrn = ptrn.replace(r'^\s*$', np.nan, regex=True)
    st.dataframe(ptrn)

    st.markdown('---')

if st.button('Search'):

    data = load_data('_'.join(data_option.split(' ')))

    filtered_data_word_level = word_level_filter(data, diphthongs=contains_diphthong, characters=character_length, phonemes=phoneme_length, syllables=syllables)

    if mode_option == 'begins with':
        try:
            matches = begins_with_pattern(filtered_data_word_level, st.session_state.ptrn_phonemes)
            st.dataframe(matches.drop(columns=['features']))
        except:
            st.text('No matches found.')
    elif mode_option == 'ends with':
        try:
            matches = ends_with_pattern(filtered_data_word_level, st.session_state.ptrn_phonemes)
            st.dataframe(matches.drop(columns=['features']))
        except:
            st.text('No matches found.')
    elif mode_option == 'exactly matches':
        try:
            matches = exactly_matches_pattern(filtered_data_word_level, st.session_state.ptrn_phonemes)
            st.dataframe(matches.drop(columns=['features']))
        except:
            st.text('No matches found.')
    elif mode_option == 'contains':
        try:
            matches = contains_pattern(filtered_data_word_level, st.session_state.ptrn_phonemes)
            st.dataframe(matches.drop(columns=['features']))
        except:
            st.text('No matches found.')
else:
    pass