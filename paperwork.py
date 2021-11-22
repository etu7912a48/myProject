#original modules
import logging
import os, re
import shutil
from datetime import datetime

#customized modules
import processor


#built the main logger for check the whole process
pw_logger = logging.getLogger('paperwork')
pw_logger.setLevel(logging.DEBUG)

log_name = datetime.now().strftime('%Y-%m-%d')
file_handler = logging.FileHandler('log/{}.log'.format(log_name))
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('[%(asctime)s][%(levelname)s] - %(name)s: %(message)s')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

pw_logger.addHandler(file_handler)
pw_logger.addHandler(stream_handler)

def func_info(func):
    def wrap(*args, **kwargs):
        pw_logger.info('Start to do - {}'.format(func.__name__))
        func(*args, **kwargs)
        pw_logger.info('Finished - {}'.format(func.__name__))
    return wrap

#the mani codes should begin here
pw_logger.info('paperwork is awake')

#set environment variants
cwd = os.curdir
input_dir = '{}/input'.format(cwd)
output_dir = '{}/output'.format(cwd)
error_dir = '{}/error'.format(cwd)

trash_can = datetime.now().strftime('%Y-%m-%d')
try:
    os.makedirs('{}/trash/{}'.format(cwd, trash_can))
except:
    pass
trash_dir = '{}/trash/{}'.format(cwd, trash_can)

#built the main processor
pw_logger.info('Set the main processor')
p = processor.Processor(data_type='DR' ,input_dir = input_dir, output_dir = output_dir, error_dir = error_dir)
p_core = processor.PDF_core()
i_core = processor.IMG_core()
o_core = processor.OCR_core()
p.set_pdfCore(p_core)
p.set_imgCore(i_core)
p.set_ocrCore(o_core)

#the workflow
print('Start to classify and rename pdf')
pdf_list = list(filter(lambda f: re.compile(r'.*.pdf').match(f), os.listdir(input_dir)))
pw_logger.info(r'{} pdf have been detected from {}.'.format(len(pdf_list), input_dir))
pw_logger.info(r'The list of pdf is {}.'.format(pdf_list))
img_list = p.convert_pdf(pdf_list)

pw_logger.info('start to refine img')
result_list = p.refine_img(img_list)

pw_logger.info('OCR is working now')
p.classify_img(result_list)

pw_logger.info('the progress has been done')


#the last work
@func_info
def move_toTrashCan(files, input_path , trash_path):
    pw_logger.info('start to clean the input dir')
    for f in files:
        shutil.move(input_path+'/'+f, trash_path+'/'+f)
    pw_logger.info('all pdf has been remove.')


#move_toTrashCan(pdf_list, input_path=input_dir, trash_path=trash_dir)

print('All progress has been done! Now, you can close this window.')
print('')
print('---IMPORTANT---')
print('please remove all pdf in the input dir to make sure it empty')
print('Please, press any key to close this window.')

t = input()
