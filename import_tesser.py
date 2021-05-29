import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
# from tqdm.notebook import tqdm
import pandas as pd
from multiprocessing import cpu_count, Pool
import tesserocr
import numpy as np

from langdetect import detect

path = './reports'

def get_filepaths():
    pdf_filepaths = []
    for root, directories, files in os.walk(path, topdown=False):
        for name in files:
            if name[-4:] == '.pdf':
                pdf_filepaths.append(os.path.join(root, name))
    return pdf_filepaths

# https://towardsdatascience.com/extracting-text-from-scanned-pdf-using-pytesseract-open-cv-cd670ee38052
# https://pdf2image.readthedocs.io/en/latest/reference.html
# this is also getting the page number because of performance reasons
def save_as_image(filepath):
    pages = convert_from_path(filepath)
    for p in range(len(pages)):
        path = filepath[:-4] + '_' + str(p) + '.jpg'
        # only save if file does not exist
        if (os.path.isfile(path) == False):
            pages[p].save(path, 'JPEG')
        else:
            break
    return len(pages)

def get_language(path):
        text = ''
        for p in range(0,5):
            image_path = path[:-4] + '_' + str(p) + '.jpg'
            if os.path.isfile(image_path):
                # pil_image = Image.open(image_path)
                # tess_api.SetImage(pil_image)
                # text += tess_api.GetUTF8Text()
                text += tesserocr.file_to_text(image_path)
            else:
                break
        return detect(text[:500]) # returns i.e en or de

def text_from_ocr(df) -> pd.DataFrame:
    rows = len(df)
    #for index, row in df.iterrows():
    for index, row in df.iterrows():
        print(str(index)+'/'+str(rows) + ' Pdf')
        text = ''
        # get initial text to apply language detection to
        pages = row['number_of_pages']
        lang = row.lang
        for page in range(pages):
            print(str(page)+'/'+ str(pages) + 'Pages')
            filepath = row['filepath'][:-4] + '_' + str(page) + '.jpg'
            text += tesserocr.file_to_text(filepath, lang=lang)
        df.loc[index, 'text'] = text
        print(index)
    return df

# https://towardsdatascience.com/make-your-own-super-pandas-using-multiproc-1c04f41944a1#6028
def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

# Initialize dataframe with filepaths
reports = pd.DataFrame(get_filepaths(), columns = ['filepath'])
reports.head()

# convert pdfs to images and save number of pages in a column
if (True):
    #reports['number_of_pages'] = reports['filepath'].apply(lambda fp: save_as_image(fp))
    reports['number_of_pages'] = reports.filepath.map(save_as_image)

# Identify language based on sample of pages
reports['lang'] = reports['filepath'].map(get_language)

# Map language codes to be tesseract compatible
reports.lang = reports.lang.map({'en':'eng','de':'deu'})

reports_de = parallelize_dataframe(reports[(reports['lang'] == 'deu')], text_from_ocr, len(os.sched_getaffinity(0)))
reports_de.to_csv('reports_de.csv')
print('Saved german reports')
reports_en = parallelize_dataframe(reports[(reports['lang'] == 'eng')], text_from_ocr, len(os.sched_getaffinity(0)))
reports_en.to_csv('reports_en.csv')
print('Saved english texts')

reports_joined = reports_de.append(reports_en)
reports_joined.to_csv('reports_tesser.csv')
#reports.to_csv('reports.csv')