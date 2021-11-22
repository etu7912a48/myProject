import fitz
import cv2
import numpy as np
import easyocr
import re
import logging

#mod  logger
m_logger = logging.getLogger('paperwork.processor')


#class of the main processor
class Processor():
    def __init__(self, data_type, *args, **kwargs) -> None:
        self.logger = logging.getLogger('paperwork.processor.Processor')

        self.input_dir = kwargs['input_dir']
        self.output_dir = kwargs['output_dir']
        self.error_dir = kwargs['error_dir']
        self.data_type = data_type

        self.logger.info('input_dir is {}'.format(self.input_dir))
        self.logger.info('output_dir is {}'.format(self.output_dir))
        self.logger.info('error_dir is {}'.format(self.error_dir))
        self.logger.info('data_type is {}'.format(self.data_type))

    def set_dataType(self, d):
        self.data_type = d

    #pdf core
    def set_pdfCore(self, p):
        self.pdf_core = p
        if self.data_type != None:
            self.pdf_core.data_type = self.data_type

    def convert_pdf(self, pdf_list):
        try:
            self.logger.info('start to convert pdf')
            p = self.pdf_core.convert_pdf(pdf_list, self.input_dir)
            return p
        except:
            self.logger.warning('some error happened when converting pdf')

    #img core
    def set_imgCore(self, i):
        self.img_core = i
        if self.data_type != None:
            self.pdf_core.data_type = self.data_type

    def refine_img(self, img_list):
        try:
            return self.img_core.refine_img(img_list)
        except:
            self.logger.warning('some error happened when refining img')

    #ocr core
    def set_ocrCore(self, o):
        self.ocr_core = o
        if self.output_dir != None:
            self.ocr_core.output_dir = self.output_dir

    def classify_img(self, img_list):
        try:
            self.ocr_core.classify_img(img_list, self.output_dir, self.error_dir)
            self.logger.info('All img has been classified')
        except:
            self.logger.warning('some error happened when doing classification of img', exc_info=True)


# sub cores of the main processor including pdf, img and ocr
class PDF_core():
    def __init__(self, *args, **kwargs) -> None:
        self.logger = logging.getLogger('paperwork.processor.PDF_core')
        self.data_type = "DR"

    def convert_pdf(self, pdf_list, input_dir):
        img_list = []
        pdfs = list(map(lambda f: fitz.open('{}/{}'.format(input_dir, f)), pdf_list))
        for pdf in pdfs:
            for  page in pdf:
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                img_list.append(img)
        return img_list


class IMG_core():
    def __init__(self, *args, **kwargs) -> None:
        self.logger = logging.getLogger('paperwork.processor.IMG_core')
        self.data_type = "DR"

    def refine_img(self, img_list):
        self.logger.info('start to refine img')
        th_list = []
        for img in img_list:
            ori = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGBA2BGR)
            gray = cv2.cvtColor(ori, cv2.COLOR_BGR2GRAY)
            k = np.ones((2, 2), np.uint8)
            close_img = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, k)
            th = cv2.adaptiveThreshold(close_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            th_list.append(th)
        return th_list


class OCR_core():
    def __init__(self) -> None:
        self.logger = logging.getLogger('paperwork.processor.OCR_core')
        self.reader = easyocr.Reader(['en'])

    def classify_img(self, img_list, output_dir, error_dir):
        problem_count = 0
        for i in img_list:
            temp_i = i[160:290, 320:720]

            text_list = self.reader.readtext(temp_i, detail=0)
            fn = list(filter(lambda o :re.compile(r'\d{12,}').findall(o), text_list))

            #pytesseract.pytesseract.tesseract_cmd=r'Tesseract-OCR/tesseract.exe'
            #s = pytesseract.image_to_string(temp_i, lang='eng')
            #fn = re.compile(r'\d{12}').findall(s)

            if fn == []:
                problem_count = problem_count + 1
                cv2.imwrite(r'{}/error-{}.png'.format(error_dir, problem_count), i)
                self.logger.warning(r'failed to recognize the delivery receipt')
                self.logger.warning(r'OCR detected those things: {}'.format(text_list))
            else:
                cv2.imwrite(r'{}/{}.png'.format(output_dir, fn[0]), i)
        if problem_count > 0:
            self.logger.warning('Detect {} files with error . Please cheeck error dir to rename those files manual'.format(problem_count))

if __name__ == '__main__':
    m_logger.warning('the module processor has been executed')



