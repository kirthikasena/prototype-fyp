# -*- coding: utf-8 -*-
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain import PromptTemplate
from torch import cuda, bfloat16
import transformers
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

# Commented out IPython magic to ensure Python compatibility.
# %pip install --upgrade --quiet huggingface_hub

HUGGINGFACEHUB_API_TOKEN = 'token'

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.001, do_sample=True, token=HUGGINGFACEHUB_API_TOKEN
)

df=pd.read_excel(filePath)


def get_intermediate_output(llm, review, aspect):
    prompt_=PromptTemplate(
    input_variables=['review','aspect'],
    template=template_
  )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.run({'review':review,'aspect':aspect})

    return prompt_summary

def get_final_output(llm, review, flow_chart, aspect):

    prompt_=PromptTemplate(
      input_variables=['flow_chart','aspect'],
      template=summarize_
    )

    prompt_chain=LLMChain(llm=llm,prompt=prompt_)
    prompt_summary=prompt_chain.run({'flow_chart':flow_chart,'aspect':aspect})

    return prompt_summary


def process_hotel_data(llm,df,aspect):
        df[f'prompt_{aspect}'] = df.apply(lambda row: get_intermediate_output( llm=llm, review=row['Reviews'],aspect=aspect), axis=1)
        df[f'summarize_{aspect}'] = df.apply(lambda row: get_final_output(llm=llm, review=row['Reviews'],flow_chart=row[f'prompt_{aspect}'],aspect=aspect), axis=1)
        # print(innovations_reasonings)
        # return df

# The columns you want to iterate over
aspects = ['food', 'Geo-context', 'Guest-relations']

for aspect in aspects:
  process_hotel_data(llm,df,aspect)

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
    "only mentions positive aspects"
]

# Mapping from DataFrame columns to simplified aspect names
column_aspect_mapping = {
    'summarize_food': 'food',
    'summarize_Geo-context': 'Geo-context',
    'summarize_Guest-relations': 'Guest-relations'
}

# Initialize a dictionary to store reviews for further processing
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


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:  # Specify the encoding here
        return file.read()

#proposed




def proposed_(text,llm,aspect):

  prompt = PromptTemplate(template=prompt_template, input_variables=["text","aspect"])

  llm_chain = LLMChain(prompt=prompt, llm=llm)

  summary=llm_chain.run({'text':text,'aspect':aspect})

  return summary

# Using the reviews_dict from your previous example:
reviews_summary_dict = {}
for aspect, reviews in reviews_dict.items():
    # Generate a summary or processed result for each aspect's reviews
    result = proposed_(reviews, llm,aspect)
    # Store the result in a new dictionary using a dynamic key
    reviews_summary_dict[f'{aspect}_summary'] = result

for aspect_summary, result in reviews_summary_dict.items():
    print(f'{aspect_summary}: {result}')





def get_final_output(llm, country, summary):

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
    innovations = innovation_chain.run({'country':country, 'prompt': summary})
    reasoning = reasoning_chain.run({'innovations': innovations, 'summary': summary})
    return final_output_format(innovations, reasoning)

#summary could be 'summary\n' or ' summary' or normal 'summary'
def process_hotel_data(llm,summary):

        summary=summary
        # print(food_summary)
        # print(country)


        innovations_reasonings=get_final_output(llm=llm, country=country, summary=summary)
        # print(innovations_reasonings)

        return innovations_reasonings

# Using the reviews_dict from your previous example:
reviews_strategies_dict = {}
for aspect, summary in reviews_summary_dict.items():
    # Generate a summary or processed result for each aspect's reviews
    strategy=process_hotel_data(llm,summary)
    # Store the result in a new dictionary using a dynamic key
    reviews_strategies_dict[aspect] = {
        'aspect': aspect.replace('_summary', ''),  # Removing '_summary' to get the original aspect name
        'strategy': strategy,
        'summary': summary
    }

# Now to print this new dictionary in a readable format
for aspect, data in reviews_strategies_dict.items():
    print(f'Aspect: {data["aspect"]}')
    print(f'  Strategy: {data["strategy"]}')
    print(f'  Summary: {data["summary"]}\n')