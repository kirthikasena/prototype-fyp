import json
import sys
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
import pandas as pd
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import os
from templates import template_,summarize_,prompt_template,mistral_prompt_,mistral_template_
from huggingface_hub import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.set_verbosity_error()

# Load environment variables from .env file
load_dotenv()

# Constants
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


#Initialize the mistral model
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

repo_id="mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.001,
    do_sample= True,
    model_kwargs={
        "max_length": 128,
        "token": HUGGINGFACEHUB_API_TOKEN
    }
)

def read_file(file_path):
    """
    Reads a data file into a DataFrame.
    
    Args:
        file_path (str): The path to the file.
    
    Returns:
        pd.DataFrame: The loaded data.
        
    Raises:
        ValueError: If the file format is not supported.
    """
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        # It's an Excel file
        df = pd.read_excel(file_path)
        print("Read Excel file successfully.")
    elif file_path.endswith('.csv'):
        # It's a CSV file
        df = pd.read_csv(file_path)
        print("Read CSV file successfully.")
    else:
        raise ValueError("Unsupported file type. Please upload an Excel or CSV file.")
    
    return df


def get_intermediate_output(llm, review, aspect):
    """
    Generates the individual summary for a given review and aspect using first prompt.
    
    Args:
        llm (HuggingFaceEndpoint): The Hugging Face model endpoint.
        review (str): The review text.
        aspect (str): The aspect to consider.
    
    Returns:
        str: The generated intermediate output.
    """
    prompt_=PromptTemplate(
    input_variables=['review','aspect'],
    template=template_
  )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.invoke({'review':review,'aspect':aspect})

    return prompt_summary


def get_final_output(llm,flow_chart, aspect):
    """
    Generates the inididual review summary summary from the putput of first/intermediate prompt.
    
    Args:
        llm (HuggingFaceEndpoint): The Hugging Face model endpoint.
        flowchart (str): The review analysis from prompt 1.
        aspect (str): The aspect to consider.
    
    Returns:
        str: The generated intermediate output.
    """

    prompt_=PromptTemplate(
      input_variables=['flow_chart','aspect'],
      template=summarize_
    )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.invoke({'flow_chart':flow_chart,'aspect':aspect})

    return prompt_summary


def process_hotel_data(llm,df,aspect):
        """
        individual summarization is processed in this function

        Args:
            llm (HuggingFaceEndpoint): The Hugging Face model endpoint.
            df (pd.DataFrame): The data frame containing hotel reviews.
            aspect (str): The aspect to process.
        """
        # batch transform through first prompt of indivdual summarization
        df[f'prompt_{aspect}'] = df.apply(lambda row: get_intermediate_output( llm=llm, review=row['Reviews'],aspect=aspect), axis=1)

        # batch transform through second prompt of indivdual summarization
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
    # Initialize a dictionary to store reviews, with aspects as keys
    reviews_dict = {aspect: [] for aspect in column_aspect_mapping.values()}

    # Iterate through each column specified in the mapping
    for column, aspect in column_aspect_mapping.items():
        # Iterate over the DataFrame rows
        for index, row in df.iterrows():
            # Retrieve the review text from the current column
            review_text = row[column]

            # Check if the review does NOT contain any of the exclusion phrases
            if not any(phrase in review_text for phrase in exclusion_phrases):
                # Append the review to the list in the dictionary for the corresponding aspect
                reviews_dict[aspect].append(review_text)
    
    return reviews_dict


def proposed_(text,llm,aspect):
    """
    Outputs overall summary from individual summary

    Parameters:
    - text(str): infividual summary review list negative aspects.
    - llm (HuggingFaceEndpoint): The Hugging Face model endpoint.
    - aspect (str): The aspect to process.

    Returns:
    - overall summary
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["text","aspect"])

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    summary=llm_chain.invoke({'text':text,'aspect':aspect})

    return summary

def final_output_format(innovations, reasoning):
    """
    joins two strings innovations and reasoning

    Parameters:
    - innovations(str): output from llm prompt- sustainable innovations
    - reasonings(str): reasoning for the innovations.

    Returns:
    - overall summary
    """

    return f"""

    Innovations:

    {innovations}

    ****************************************

    Reasoning:

    {reasoning}

    """


def get_final_innovations(llm, country, summary):

    """
    outputs innovation and reaoning 

    Parameters:
     llm (HuggingFaceEndpoint): The Hugging Face model endpoint.
     country(str): country of the hotel
     summary(str): overall summary from the last prompt

    Returns:
    - innovation and reasoning
    """

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

    # first prompt to trigger sustainble innovations
    innovations = innovation_chain.invoke({'country':country, 'prompt': summary})
     # first prompt to trigger  reasoning for the iinvoations
    reasoning = reasoning_chain.invoke({'innovations': innovations, 'summary': summary})
    return final_output_format(innovations, reasoning)


if __name__ == "__main__":
    file_path = sys.argv[1]
    country = sys.argv[2]

    reviews_summary_dict = {}

    # reading excel/csv file of reviews
    df= read_file(file_path)

    # individual reviews
    for aspect in aspects:
        process_hotel_data(llm,df,aspect)

    # filter negative reviews 
    reviews_dict=filter_reviews(df, column_aspect_mapping, exclusion_phrases)

    #get overall reviews
    for aspect, reviews in reviews_dict.items():
        # Generate a summary or processed result for each aspect's reviews
        result = proposed_(reviews, llm,aspect)
        # Store the result in a new dictionary using a dynamic key
        reviews_summary_dict[f'{aspect}_summary'] = result

    #change temperature of llm  for innovations and reasoning
    llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.7,
    do_sample= True,
    model_kwargs={
        "max_length": 128,
        "token": HUGGINGFACEHUB_API_TOKEN
    }
    )

    # summary and reasoning 
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

