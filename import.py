import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
# from tqdm.notebook import tqdm
import pandas as pd
from multiprocessing import cpu_count, Pool
from pytesseract import image_to_string
import numpy as np

from langdetect import detect

path = './reports'
pdf_filepaths = []

for root, directories, files in os.walk(path, topdown=False):
	for name in files:
		if name[-4:] == '.pdf':
			pdf_filepaths.append(os.path.join(root, name))

reports = pd.DataFrame(pdf_filepaths, columns = ['filepath'])
reports.head()

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

if (True):
    reports['number_of_pages'] = reports['filepath'].apply(lambda fp: save_as_image(fp))

def map_to_tesseract_languages(lang):
    if lang == 'en':
        return 'eng'
    elif lang == 'de':
        return 'deu'

def get_language(path):
        miner_text = ''
        for p in range(0,5):
            image_path = path[:-4] + '_' + str(p) + '.jpg'
            if os.path.isfile(image_path):
                miner_text += image_to_string(image_path)
            else:
                break
        lang = map_to_tesseract_languages(detect(miner_text[:500]))
        return lang

def text_from_ocr(df) -> pd.DataFrame:
    rows = len(df)
    #for index, row in df.iterrows():
    for index, row in df.iterrows():
        print(str(index)+'/'+str(rows) + ' Pdf')
        text = ''
        # get initial text to apply language detection to
        pages = row['number_of_pages']
        for page in range(pages):
            print(str(page)+'/'+ str(pages) + 'Pages')
            text += image_to_string(row['filepath'][:-4] + '_' + str(page) + '.jpg', lang=row['lang'])
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

#df_unique = pd.read_csv('captum.csv')
# reports[:4]
reports['lang'] = reports['filepath'].apply(lambda path: get_language(path))
# order by language to avoid switching between tesseract language models extensively
reports = reports.sort_values(by='lang')
reports_de = parallelize_dataframe(reports[(reports['lang'] == 'deu')], text_from_ocr, len(os.sched_getaffinity(0)))
reports_de.to_csv('reports_de.csv')
reports_en = parallelize_dataframe(reports[(reports['lang'] == 'eng')], text_from_ocr, len(os.sched_getaffinity(0)))
reports_en.to_csv('reports_en.csv')
reports_joined = reports_de.append(reports_en)
reports.to_csv('reports.csv')
reports_joined.to_csv('reports_joined.csv')