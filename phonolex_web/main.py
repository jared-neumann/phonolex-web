import pandas as pd
import streamlit as st

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

@st.cache
def word_level_filter(data, diphthongs = True, characters = (1, 20), phonemes = (1, 20), syllables = (1, 10)):

    filtered_data = data[
        (data.contains_diphthong.astype(bool) == diphthongs)
        & (data.character_length.astype(int) >= characters[0]) & (data.character_length.astype(int) <= characters[1])
        & (data.phoneme_length.astype(int) >= phonemes[0]) & (data.phoneme_length.astype(int) <= phonemes[1])
        & (data.syllables.astype(int) >= syllables[0]) & (data.syllables.astype(int) <= syllables[1])
    ]

    return filtered_data.drop(columns=['features'])

st.markdown("<h1 style='text-align: center; color: black;'>PhonoLex</h1>", unsafe_allow_html=True)

st.markdown('---')

st.markdown("<h4 style='text-align: center; color: black;'>Choose a source to search:</h4>", unsafe_allow_html=True)
data_option = st.selectbox('', ['common lemmas', 'common words', 'all words'])

data = load_data('_'.join(data_option.split(' ')))

st.markdown('---')

st.markdown("<h4 style='text-align: center; color: black;'>Define word-level features if desired:</h4>", unsafe_allow_html=True)

col_diphthong, col_characters, empty1, col_phonemes, empty2, col_syllables = st.columns([2,1,0.33,1,0.33,1])
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

st.markdown('---')

st.markdown("<h4 style='text-align: center; color: black;'>Choose a pattern-matching mode:</h4>", unsafe_allow_html=True)
mode_option = st.selectbox('', ['contains', 'begins with', 'ends with', 'exactly matches'])

st.markdown('---')

if st.button('Search'):
    filtered_data_word_level = word_level_filter(data=data, diphthongs=contains_diphthong, characters=character_length, phonemes=phoneme_length, syllables=syllables)
    st.write(filtered_data_word_level)
else:
    pass