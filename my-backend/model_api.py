# Assuming the updated Python script now accepts a country argument
import sys
import json
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
import pandas as pd
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import os
from templates import template_,summarize_,prompt_template,mistral_prompt_,mistral_template_
from huggingface_hub import logging
import os
import requests
from dotenv import load_dotenv

logging.set_verbosity_error()


# Load environment variables from .env file
load_dotenv()


aspects = ['food', 'Geo-context', 'Guest-relations']


# Step 2: Retrieve the API token from the environment variables
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
print("API Token:", HUGGINGFACEHUB_API_TOKEN) 

# List of phrases that indicate a review doesn't include specific details
exclusion_phrases = [
    "not mentioned",
    "does not mention",
    "did not mention",
    "it was not specifically mentioned",
    "not provide any specific",
    "no specific complaints",
    "not particularly impressive or memorable",
    "did not mention any specific negative experiences",
    "no negative aspects",
    "only mentions positive",
    "did not mention any negative aspects",
    "only mentions positive aspects",
    "does not mention any negative",
    "does not mention any negative experiences",
]

# Mapping from DataFrame columns to simplified aspect names
column_aspect_mapping = {
    'summarize_food': 'food',
    'summarize_Geo-context': 'Geo-context',
    'summarize_Guest-relations': 'Guest-relations'
}

# HUGGINGFACEHUB_API_TOKEN = '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'

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

# llm = HuggingFaceEndpoint(
#     repo_id=repo_id, max_length=128, temperature=0.001, do_sample=True, token=HUGGINGFACEHUB_API_TOKEN
# )

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.001,
    do_sample= True,
    model_kwargs={
        "max_length": 128,

        "token": HUGGINGFACEHUB_API_TOKEN
    }
)


def final_output_format(innovations, reasoning):
  return f"""

  Innovations:

  {innovations}

  ****************************************

  Reasoning:

  {reasoning}

  """

def get_intermediate_output(llm, review, aspect):
    prompt_=PromptTemplate(
    input_variables=['review','aspect'],
    template=template_
  )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.invoke({'review':review,'aspect':aspect})

    return prompt_summary

def get_final_output(llm,flow_chart, aspect):

    prompt_=PromptTemplate(
      input_variables=['flow_chart','aspect'],
      template=summarize_
    )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.invoke({'flow_chart':flow_chart,'aspect':aspect})

    return prompt_summary


def process_hotel_data(llm,df,aspect):
        df[f'prompt_{aspect}'] = df.apply(lambda row: get_intermediate_output( llm=llm, review=row['Reviews'],aspect=aspect), axis=1)
        df[f'summarize_{aspect}'] = df.apply(lambda row: get_final_output(llm=llm,flow_chart=row[f'prompt_{aspect}'],aspect=aspect), axis=1)

def filter_reviews(df, column_aspect_mapping, exclusion_phrases):
    """
    Filters reviews from a DataFrame based on specified aspects and exclusion phrases.
    
    Parameters:
    - df: DataFrame containing review data.
    - column_aspect_mapping: Dictionary mapping column names to aspects.
    - exclusion_phrases: List of phrases to exclude reviews containing them.
    
    Returns:
    - Dictionary with aspects as keys and lists of reviews as values, excluding
      reviews containing any of the specified exclusion phrases.
    """
    # Additional exclusion phrases for non-food aspects
    non_food_exclusions = ['menu', 'order','food']

    # Initialize a dictionary to store reviews, with aspects as keys
    reviews_dict = {aspect: [] for aspect in column_aspect_mapping.values()}

    # Iterate through each column specified in the mapping
    for column, aspect in column_aspect_mapping.items():
        # Decide exclusion list based on aspect
        if aspect != 'food':  # Apply non-food exclusions only for non-food aspects
            combined_exclusions = exclusion_phrases + non_food_exclusions
        else:
            combined_exclusions = exclusion_phrases

        # Iterate over the DataFrame rows
        for index, row in df.iterrows():
            # Retrieve the review text from the current column
            review_text = row[column]

            # Check if the review does NOT contain any of the combined exclusion phrases
            if not any(phrase in review_text for phrase in combined_exclusions):
                # Append the review to the list in the dictionary for the corresponding aspect
                reviews_dict[aspect].append(review_text)
    
    return reviews_dict


def proposed_(text,llm,aspect):

  prompt = PromptTemplate(template=prompt_template, input_variables=["text","aspect"])

  llm_chain = LLMChain(prompt=prompt, llm=llm)

  summary=llm_chain.invoke({'text':text,'aspect':aspect})

  return summary



def get_final_innovations(llm, country, summary):

    prompt_reasoning = PromptTemplate(
        input_variables=["innovations", "summary"],
        template=mistral_template_
    )

    prompt_ = PromptTemplate(
        input_variables=["country", "prompt"],
        template=mistral_prompt_
    )

    innovation_chain = LLMChain(llm=llm, prompt=prompt_)
    reasoning_chain = LLMChain(llm=llm, prompt=prompt_reasoning)
    innovations = innovation_chain.invoke({'country':country, 'prompt': summary})
    reasoning = reasoning_chain.invoke({'innovations': innovations, 'summary': summary})
    return final_output_format(innovations, reasoning)

def read_data(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")
    return df


if __name__ == "__main__":
    file_path = sys.argv[1]
    country = sys.argv[2]

    # file_path = 'C:/Users/HP/Documents/year 4/Individual Research/prototype/website/my-backend/uploads/file-1713297279660-493297330sample.xlsx'
    # country = 'Sri lanka'
    # print(f'token:{HUGGINGFACEHUB_API_TOKEN}')


    reviews_summary_dict = {}

    df=read_data(file_path)

    for aspect in aspects:
        process_hotel_data(llm,df,aspect)

    reviews_dict=filter_reviews(df, column_aspect_mapping, exclusion_phrases)

    for aspect, reviews in reviews_dict.items():
        # Generate a summary or processed result for each aspect's reviews
        result = proposed_(reviews, llm,aspect)
        # Store the result in a new dictionary using a dynamic key
        reviews_summary_dict[f'{aspect}_summary'] = result

    llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.7,
    do_sample= True,
    model_kwargs={
        "max_length": 128,

        "token": HUGGINGFACEHUB_API_TOKEN
    }
    )
    reviews_strategies_dict = {}
    for aspect, summary in reviews_summary_dict.items():
        # Generate a summary or processed result for each aspect's reviews
        strategy=get_final_innovations(llm, country, summary)
        # Store the result in a new dictionary using a dynamic key
        reviews_strategies_dict[aspect.replace('_summary', '')] = {  # Removing '_summary' to get the original aspect name
        'summary': summary,
        'strategies':strategy
    }
        
    print(json.dumps(reviews_strategies_dict))

