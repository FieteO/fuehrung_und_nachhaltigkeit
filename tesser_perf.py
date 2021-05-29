# https://github.com/sirfz/tesserocr/issues/205
# https://gist.github.com/arocketman/b74050b87a2c763e3023a1142dd70090
import concurrent.futures
import os
import queue
import time

import tesserocr
from pdf2image import convert_from_bytes

tesserocr_queue = queue.Queue()


def perform_ocr(img):
    tess_api = None
    try:
        tess_api = tesserocr_queue.get(block=True, timeout=300)
        tess_api.SetImage(img)
        text = tess_api.GetUTF8Text()
        #print('OCR performed')
        return text
    except tesserocr_queue.Empty:
        print('Empty exception caught!')
        return None
    finally:
        if tess_api is not None:
            tesserocr_queue.put(tess_api)


def run_performance_test(ocr_images, num_threads):
    # Setup Queue
    for _ in range(num_threads):
        tesserocr_queue.put(tesserocr.PyTessBaseAPI())

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


if __name__ == '__main__':
    # Pdf to image
    pdf = './reports/scraped/full/freseniusmedicalcare.pdf'
    with open(pdf, 'rb') as raw_pdf:
        ocr_entities = convert_from_bytes(raw_pdf.read(), dpi=300, thread_count=4, grayscale=True)

    # for i in range(1, 9):
    #     print(f'Starting performance test with {i} threads')
    #     result, total_time = run_performance_test(ocr_entities, i)
    #     print(f'Performed test with {i} threads and took {str(total_time)} time')
    #     print(result[:500])
    threads = 2
    print(f'Starting performance test with {threads} threads')
    result, total_time = run_performance_test(ocr_entities, threads)
    print(f'Performed test with {threads} threads and took {str(total_time)} time')
    text = ""
    print(sum(1 for item in result))
    for item in result:
        text += item
    print(text)
    #print(result[:500])