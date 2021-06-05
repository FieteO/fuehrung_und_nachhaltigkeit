import os
import re
import pandas as pd
from typing import Tuple
# https://github.com/sirfz/tesserocr/issues/205
# https://gist.github.com/arocketman/b74050b87a2c763e3023a1142dd70090
import concurrent.futures
import queue
import time

import tesserocr
from pdf2image import convert_from_bytes
from langdetect import detect

tesserocr_queue = queue.Queue()

def get_filepaths(path):
    pdf_filepaths = []
    for root, directories, files in os.walk(path, topdown=False):
        for name in files:
            if name[-4:] == '.pdf':
                pdf_filepaths.append(os.path.join(root, name))
    return pdf_filepaths

def get_language(path):
        text = ''
        for p in range(0,5):
            image_path = path[:-4] + '_' + str(p) + '.jpg'
            if os.path.isfile(image_path):
                if len(text) <= 500:
                    text += tesserocr.file_to_text(image_path)
                else:
                    print('Reached required number of words for language detection after ' + str(p) + ' pages.')
                    break
            else:
                break
        return detect(text[:500]) # returns i.e en or de


def perform_ocr(img):
    tess_api = None
    try:
        tess_api = tesserocr_queue.get(block=True, timeout=300)
        tess_api.SetImage(img)
        text = tess_api.GetUTF8Text()
        return text
    except tesserocr_queue.Empty:
        print('Empty exception caught!')
        return None
    finally:
        if tess_api is not None:
            tesserocr_queue.put(tess_api)


def run_threaded_ocr_on_pdf(ocr_images, num_threads, language):
    # Setup Queue
    for _ in range(num_threads):
        tesserocr_queue.put(tesserocr.PyTessBaseAPI(lang=language))

    # Perform OCR using ThreadPoolExecutor
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        res = executor.map(perform_ocr, ocr_images)
    end = time.time()

    # Restoring queue
    for _ in range(num_threads):
        api = tesserocr_queue.get(block=True)
        api.End()

    tesserocr_queue.queue.clear()
    return (res, end - start)

def ocr_pdf(filepath: str, language: str, threads: int) -> Tuple[str, int]:
    # Pdf to image
    with open(filepath, 'rb') as raw_pdf:
        ocr_entities = convert_from_bytes(raw_pdf.read(), dpi=300, thread_count=4, grayscale=True)

    print(f'Starting OCR for file { os.path.basename(filepath) }')
    result_iterator, total_time = run_threaded_ocr_on_pdf(ocr_entities, threads, language)

    text = ''
    number_of_pages = 0
    for item in result_iterator:
        text += item
        number_of_pages += 1
    
    print(f'OCR finished in {str(total_time)} seconds with an average of {str(total_time / number_of_pages)} seconds per page.')
    return text, number_of_pages

def clean_text(text: str) -> str:
    # https://www.kaggle.com/arijzou/text-preprocessing-disaster-tweets
    url_pattern = r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
    # https://www.emailregex.com/
    email_pattern = r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''
    text = text.replace("\n"," ")                   # new lines
    text = " ".join(text.split())                   # consecutive spaces
    text = re.sub(url_pattern, '', text)            # urls
    text = re.sub(email_pattern, '', text)          # e-mails
    text = re.sub(r'[:°<>,="”~{}()!\[\]]','', text)                # meaningless characters
    text = text.replace(':', '')                    # colons
    text = text.lower()                             # turn lowercase
    return text


if __name__ == '__main__':
    output_file = 'reports.csv'
    # read in reports with ocr if csv does not exist already
    if os.path.isfile(output_file) == False:
        # check optimal number of threads with tesser_perf.py
        threads = 8
        root = './reports'
        # Initialize dataframe with filepaths
        reports = pd.DataFrame(get_filepaths(root), columns = ['filepath'])

        # Identify language based on sample of pages
        reports['lang'] = reports['filepath'].map(get_language)
        reports.lang = reports.lang.map({'en':'eng','de':'deu'})
        reports = reports.sort_values(by='lang')
        reports.reset_index(drop=True, inplace=True)
        
        for index, row in reports.iterrows():
            text, number_of_pages = ocr_pdf(row.filepath, row.lang ,threads)
            reports.loc[index, 'text'] = text
            reports.loc[index, 'number_of_pages'] = number_of_pages

        reports.number_of_pages = reports.number_of_pages.astype(int)   # is decimal otherwise
        print(reports.head())
        reports.to_csv(output_file)
    
    reports = pd.read_csv(output_file, index_col=0)
    reports['text'] = reports['text'].map(clean_text)
    reports.to_csv(output_file)
