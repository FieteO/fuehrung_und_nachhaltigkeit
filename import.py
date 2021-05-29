import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
# from tqdm.notebook import tqdm
import pandas as pd
from multiprocessing import cpu_count, Pool
import numpy as np
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

def ocr_pdf(filepath, language, threads):
    # Pdf to image
    with open(filepath, 'rb') as raw_pdf:
        ocr_entities = convert_from_bytes(raw_pdf.read(), dpi=300, thread_count=4, grayscale=True)

    print(f'Starting OCR for file { os.path.basename(filepath) }')
    result_iterator, total_time = run_threaded_ocr_on_pdf(ocr_entities, threads, language)

    text = ''
    number_of_pages = sum(1 for item in result_iterator)
    for item in result_iterator:
        text += item
    
    print(f'OCR finished in {str(total_time)} seconds with an average of {str(total_time / number_of_pages)} seconds per page.')
    print('Text: ' + text)
    return (text, number_of_pages)


if __name__ == '__main__':
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

    reports.to_csv('reports.csv')