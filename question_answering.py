from typing import Tuple
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import transformers

filepath = 'reports/siemens_report'
# Read text
with open(filepath) as file:
    text = file.read()

text = text.replace(r"\n"," ")

pretrained_model = "valhalla/longformer-base-4096-finetuned-squadv1"

# Initialize the tokenizer
tokenizer: transformers.LongformerTokenizerFast = AutoTokenizer.from_pretrained(pretrained_model)

# Initialize the model
# model = AutoModelForQuestionAnswering.from_pretrained(pretrained_model)
answering_pipeline = transformers.pipeline('question-answering', model=pretrained_model, tokenizer=pretrained_model)

def answer_question(question, text):
    answers = []
    text = text.split()
    chunk_size = 1800
    text = text[:round(len(text)/9)]
    # print("Iterations: " + str(round(len(text) / chunk_size)))
    for i in range(0, len(text), chunk_size):
        if i+chunk_size < len(text):
            chunk = ' '.join(text[i:i+chunk_size])
            #print("Extected token length: " + str(len(tokenizer.encode(chunk))))
        else:
            chunk = ' '.join(text[i:len(text)])

        if len(tokenizer.encode(question)) + len(tokenizer.encode(chunk)) <= 4096:

            result = answering_pipeline(question=question, context=chunk)
            answer = result['answer']
            confidence = result['score']

            if confidence > .75:
                answers.append((answer, confidence))
    return answers
        

company = "Siemens"
questions = [
    f"Does { company } commit to cut it's carbon emissions?",
    f"When will { company } be carbon neutral?",
    f"How many women are in leading positions at { company }?",
    f"Will { company } work on establishing an inclusive company culture?",
    f"Does { company } commit to exclusively use green energy in the future?",
]

for question in questions:
    print(question)
    print(answer_question(question, text))

# question = f"Does { company } commit to cut it's carbon emissions?"
# print(question)
# print(answer_question(question, text))
# question = f"When will { company } be carbon neutral?"
# print(question)
# print(answer_question(question, text))
# question = f"How many women are in leading positions at { company }?"
# print(question)
# print(answer_question(question, text))
# question = f"Will { company } invest in renewable energies?"
# print(question)
# print(answer_question(question, text))
# question = f"Will { company } work on establishing an inclusive company culture?"
# print(question)
# print(answer_question(question, text))
# question = f"Does { company } commit to exclusively use green energy in the future?"
# print(question)
# print(answer_question(question, text))