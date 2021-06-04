from typing import TypedDict, List
# import torch
from transformers import AutoTokenizer, LongformerTokenizerFast, pipeline, QuestionAnsweringPipeline

pretrained_model = "valhalla/longformer-base-4096-finetuned-squadv1"
filepath = 'reports/siemens_report'
company = "Siemens"
questions = [
    # f"Does { company } commit to cut it's carbon emissions?",
    f"When will { company } be carbon neutral?",
    # f"How many women are in leading positions at { company }?",
    # f"Does { company } work on establishing an inclusive company culture?",
    # f"Does { company } commit to exclusively use green energy in the future?",
]
number_of_answers=3

# Read text
with open(filepath) as file:
    text = file.read()

text = text.replace(r"\n"," ")

# Initialize the model
# https://huggingface.co/transformers/main_classes/pipelines.html
answering_pipeline = pipeline('question-answering', model=pretrained_model, tokenizer=pretrained_model)     
            
# Dictionary as returned by calling answering_pipeline()
Result = TypedDict('Result', {'score':float, 'start':int, 'end':int, 'answer':str})

# https://huggingface.co/transformers/main_classes/pipelines.html#transformers.QuestionAnsweringPipeline.__call__
results: List[Result] = answering_pipeline(question=questions, context=text, topk=number_of_answers, max_seq_len=4096, max_answer_len=20)

# for result in results:
#     print(result)
#     print(result['answer'])
#     print(result['score'])

import math

for i in range(len(results)):
    q = math.trunc(i/number_of_answers) # number that increases only every fifth i (0.2 -> 0, ..., 0.8 -> 0, 1 -> 1)
    # print the question only once for each answer block
    if i % number_of_answers == 0:
        print(questions[q])
        print("-"*50)
    result = results[i]
    print(result['answer'])
    #print(str(result['answer']) + " - " + str(result['score']))
# print(result['answer'])
# print(result['score'])