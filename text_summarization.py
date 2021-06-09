import pandas as pd
import nltk
import math
from transformers import pipeline

# nltk.download()

pretrained_model = "valhalla/longformer-base-4096-finetuned-squadv1"
filepath = 'reports/siemens_report'

# Read text
reports = pd.read_csv('reports.csv')

# https://huggingface.co/transformers/main_classes/pipelines.html#transformers.SummarizationPipeline
summary_pipeline = pipeline('summarization')

# generate chunks of text \ sentences <= 1024 tokens
def nest_sentences(document):
    nested = []
    sent = []
    length = 0
    for sentence in nltk.sent_tokenize(document):
        if len(sentence) > 1024:
            number_of_splits = math.ceil(len(sentence) / 1024) # round up
            for i in range(number_of_splits):
                chunk = sentence[i*1024:(i+1)*1024]
                # append straight to nested
                if len(chunk) == 1024:
                    sent.append(chunk)
                    nested.append(sent)
                    sent = []
                    length = 0
                # else:
                    # sent.append(chunk)  # just append it there may be space left for more
        # the else chunk will get lost here (but better than the previous version that skipped sentences > 1024)
        if length + len(sentence) <= 1024:
            sent.append(sentence)
            length += len(sentence)
        else:
            nested.append(sent)
            sent = []
            length = 0
    return nested

# generate summary on text with <= 1024 tokens
def generate_summary(nested_sentences):
    summaries = []
    for nested in nested_sentences:
        text = ""
        for sentence in nested:
            text += sentence
        if len(text) > 142:
            output = summary_pipeline(text, return_text=True)
            for out_dict in output:
                summaries.append(f"-{ out_dict['summary_text'] } \n\n")

    summaries = ' '.join(summaries)
    return summaries

nested_sentences = nest_sentences(reports['text'][6])
summaries = generate_summary(nested_sentences)
print(summaries)




# Dictionary as returned by calling answering_pipeline()
# Result = TypedDict('Result', {'score':float, 'start':int, 'end':int, 'answer':str})

# https://huggingface.co/transformers/main_classes/pipelines.html#transformers.QuestionAnsweringPipeline.__call__
# https://discuss.huggingface.co/t/summarization-on-long-documents/920/6#post_7
# results = summary_pipeline(text, min_length=int(len(text)/4), return_text=True) # : List[Result]
# print(results)

# for result in results:
#     print(result)
#     print(result['answer'])
#     print(result['score'])

#import math
# for i in range(len(results)):
#     q = math.trunc(i/number_of_answers) # number that increases only every fifth i (0.2 -> 0, ..., 0.8 -> 0, 1 -> 1)
#     # print the question only once for each answer block
#     if i % number_of_answers == 0:
#         print(questions[q])
#         print("-"*50)
#     result = results[i]
#     print(result['answer'])
    #print(str(result['answer']) + " - " + str(result['score']))
# print(result['answer'])
# print(result['score'])