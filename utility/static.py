import datetime
import zipfile
from utility.setting import DB_STG, OPENAPI_PATH


def now():
    return datetime.datetime.now()

def strf_time(timetype, std_time=None):

    if std_time is None:
        str_time = now().strftime(timetype)
    else:
        str_time = std_time.strftime(timetype)
    return str_time

def read_enc(trcode):
    enc = zipfile.ZipFile(f'{OPENAPI_PATH}/data/{trcode}.enc')
    lines = enc.read(trcode.upper() + '.dat').decode('cp949')
    return lines


def parse_dat(trcode, lines):
    lines = lines.split('\n')
    start = [i for i, x in enumerate(lines) if x.startswith('@START')]
    end = [i for i, x in enumerate(lines) if x.startswith('@END')]
    block = zip(start, end)
    enc_data = {'trcode': trcode, 'input': [], 'output': []}
    for start, end in block:
        block_data = lines[start - 1:end + 1]
        block_info = block_data[0]
        block_type = 'input' if 'INPUT' in block_info else 'output'
        record_line = block_data[1]
        tokens = record_line.split('_')[1].strip()
        record = tokens.split('=')[0]
        fields = block_data[2:-1]
        field_name = []
        for line in fields:
            field = line.split('=')[0].strip()
            field_name.append(field)
        fields = {record: field_name}
        enc_data['input'].append(fields) if block_type == 'input' else enc_data['output'].append(fields)
    return enc_data

def timedelta_sec(second, std_time=None):
    if std_time is None:
        next_time = now() + datetime.timedelta(seconds=second)
    else:
        next_time = std_time + datetime.timedelta(seconds=second)
    return next_time
