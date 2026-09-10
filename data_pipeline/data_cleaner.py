import config as cfg
import pandas as pd
# --------------------------------------------------------------------------
# 1. clean ratings
def convert_words_to_numbers(text):
    """
    Convert words to numbers in a given text.
    Args:    text (str): The input text containing words to be converted.
     """
    word_to_number = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    return word_to_number.get(text.lower(), text)
       
def clean_ratings_data(dirty_data):
    """
    Clean the ratings data by converting words to numbers.
    """
    dirty_data["rating"] = dirty_data["rating"].apply(convert_words_to_numbers)
    return dirty_data

#-----------------------------------------------------------------------------
# 2. clean price column
def clean_price_data(dirty_data):
    '''
    Â£47.82 --> 47.82
    rename column price to price_gbp
    '''
    dirty_data["price"] = dirty_data["price"].str.replace("Â£", "").astype(float)
    dirty_data = dirty_data.rename(columns={"price": "price_gbp"})
    return dirty_data

#-----------------------------------------------------------------------------
# 3. clean availability column
def clean_availability_data(dirty_data):
    '''
    Convert availability values to boolean.
    '''
    dirty_data["availability"] = dirty_data["availability"].apply(lambda x: True if x.strip().lower() == "In Stock".lower() else False)
    return dirty_data

#-----------------------------------------------------------------------------
# 4. convert price from GBP to INR
def convert_gbp_to_inr(dirty_data):
    '''
    Convert price from GBP to INR using a conversion rate.
    '''
    conversion_rate = cfg.GBP_TO_INR_CONVERSION_RATE
    dirty_data["price_inr"] = dirty_data["price_gbp"] * conversion_rate
    return dirty_data

# ----------------------------------------------------------------------------
# main
def clean_books_data(raw_data):
    data_to_clean = raw_data.copy()
    data_to_clean=clean_ratings_data(data_to_clean)
    data_to_clean=clean_price_data(data_to_clean)
    data_to_clean=clean_availability_data(data_to_clean)

    data_to_clean=convert_gbp_to_inr(data_to_clean)

    clean_data = data_to_clean.copy()
    return clean_data

