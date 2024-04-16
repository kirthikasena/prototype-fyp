template_="""

[SYS]
you are honest and critical decision maker and expert in flow chart decision making
[/SYS]


[INST]
Objective :think step by step  following the flowchart guidance below to identify and summarize negative aspects of {aspect} of the hotel in the review with evidence
Make sure to give the summary at the end , don't take much time
Note:
Don't assume until critically analyzed correctely and DON't hallucinate, truthful information is required

review:{review}


keep a list of {aspect}-related meaning in mind and begin the analysis:
Step 1 : Identify the overall sentimnet of the review step by step by asking questions and answering them :
Step 2 :Generate questions based on{aspect} and answer them to  solve this whether the the review contain {aspect} words step by step:
Step 3 :Generate questions based {aspect} and answer to self-evalaute whther the identified keywords actually represent {aspect}:

Final Output:
[thinking process based on {aspect} aspect only]
[Rectangle - Summary]: [Based on the thinkin gprocess and answers ,Provide the generated summary on the negative aspect of {aspect} or state the {aspect} was not mentioned or positive]
[Rectangle - evidence and reasoning]: [quote phrases/issues from the review as evidence]

[/INST]

"""


summarize_="""
[INST]
State the negative aspect of the {aspect}. give in one sentence based on review analysis(last step)
BE direct

review analysis:
{flow_chart}

output FORMAT:
[Statement]: [statement if {aspect} mentioned or not mentioned with their sentiment , give evidance, avoid redundancies ]

[/INST]

"""

prompt_template = """

[SYS]
you are critical prioritizer
[/SYS]

[INST]

review:{text}

find reviews from the above  and summarize those that mention about {aspect} concerns based on the frequenc of a particular concern higher to lowest

[/INST]

"""



"""### Strategies"""


mistral_prompt_="""
[SYS]
You are creative expert in sustainability in hosplitality industy
[/SYS]
[INST]
Solve this issue at hotel with aspect of sustainability.Combine the uncombinable  .Explore a 'what if' moment in history for this {country} hotel
Give examples
Let’s think divergently to combine the hospitality ideas with sustainability , imagine new ideas step by step relevant to the summary
Attract people all over the world
YOU MUST ONLY GIVE 4 STRATEGIES that is very relavent to the summary AND NO MORE

problem:{prompt}

------------------------------------------------------

output format:
Solution:[ONLY 4 what if innovations VERY RELAVENT TO THE SUMMARY]


[/INST]
"""

mistral_template_="""
[SYS]
You are a critical and creative and truthful reasoner
[/SYS]
[INST]

1.Check relavence of the innovation to the solution
2. Give reasoning based on the innovation given
3. why this innovation is given
4.what would it lead to? and reasoning based on how it adresses the issue in the summary given
5. The most relevant innovation should be ordered first


summary :{summary}

innovation solution:{innovations}
------------------------------------------------------

output format:
reasoning :[reasoning on why this innovation solution]


[/INST]
"""




