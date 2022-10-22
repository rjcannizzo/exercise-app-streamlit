"""
Tools for working with the csv library.
2020-08-02
"""
import chardet
from chardet.universaldetector import UniversalDetector
import csv
from pathlib import Path
import pandas as pd

def dialect_report(dialect):
    """
    Prints the formatting parameters of a dialect.
    :param dialect: csv Dialect class
    :return: None
    """
    print(
        f"delimiter = {repr(dialect.delimiter)}\n"
        f"doublequote = {dialect.doublequote}\n"
        f"lineterminator = {repr(dialect.lineterminator)}\n"
        f"quotechar = {dialect.quotechar}\n"
        f"skipinitialspace = {dialect.skipinitialspace}\n"
    )


def detect_header(filepath):
    """
    Return True if the file appears to have a header, else False.
    :param filepath: full directory to the file
    :return: Bool
    """
    with open(filepath) as f:
        sample = f.read(1024)
        return csv.Sniffer().has_header(sample)


def detect_dialect(filepath):
    """
    Return a csv Dialect object - the best guess as to a file's dialect.
    :param filepath: full directory to the file
    :return: csv dialect
    """
    with open(filepath) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        return dialect


def write_csv(filepath, header=None, data=None, encoding='utf-8'):
    """
    Write a csv file with the specified encoding.
    :param encoding: default encoding is utf-8
    :param filepath: name and directory of csv file to write
    :param header: optional header as list
    :param data: iterable containing data to write
    :return: None
    """
    with open(filepath, 'w', newline='', encoding=encoding) as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(data)


def csv_dictreader(filepath, fieldnames=None, encoding='utf-8', errors='strict'):
    """
    Yield rows from a csv processed by DictReader.
    :param filepath: the filename to process
    :param fieldnames: optional fieldnames (header row). Defaults to 1st row in file.
    :param encoding: default is utf-8
    : param errors: determines how errors are handled. strict raises an exception. Use 'ignore' to bypass bad bytes.
    :yield: DictReader row object (ordered dict)
    """
    with open(filepath, encoding=encoding) as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        for row in reader:
            yield row


def append_csv(filepath, data):
    """
    Write data to the specified csv file.
    :param file_name: directory and filename of csv file to append data to.
    :param data: data to be written. Automatically converted to a list, if necessary
    :return: None
    """
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def get_date_seperator(date_str):
    """
    Return the date separator found in the input string.
    Helper utility for correct_date_format.
    :param date_str: string
    :return: string
    """
    if '-' in date_str:
        return '-'
    return '/'

def fix_date_str(date_str, seperator):
    """
    Return a date string formatted as 'YYYY-MM-DD'.
    Helper utility for correct_date_format.
    WARNING: CANNOT PROCESS DATETIMES; MUST REMOVE THE TIME, TIMEZONE, ETC.
    :param date_str: a string representing a date
    :param seperator: the separator used in the date string
    :return: string
    """
    parts = date_str.split(seperator)
    if len(parts[0]) == 4:
        return '-'.join(parts)
    else:
        reordered_parts = [parts[-1], parts[0], parts[1]]
        return '-'.join(reordered_parts)

def correct_date_columns_pd(input_csv, date_columns, remove_time=False, header_rows='infer', encoding='utf-8'):
    """
    Return a DataFrame with the date columns converted to Pandas datetime type.
    Date columns are specified in the date_columns parameter.
    Created to facilitate working with SQLite date columns.
    :param input_csv: full directory to the csv file to process.
    :param date_columns: an iterable of column names or indexes (integers). Do NOT mix types!
    :param remove_time: removes the time portion of the datetime if True.
    :param header_rows: Row number(s) to use as the column names. Default behavior is to infer the column names.
    :param encoding: file encoding. Defaults to UTF-8.
    :return: DataFrame
    """

    def determine_date_column_type():
        """
        Retun the method needed to select the data columns.
        Returns df.iloc for integers, df.loc for strings
        :return: Pandas DataFrame method
        """
        if all([isinstance(x, int) for x in date_columns]):
            return df.iloc
        else:
            return df.loc

    df = pd.read_csv(input_csv, header=header_rows, encoding=encoding)

    col_getter = determine_date_column_type()
    for col in date_columns:
        if remove_time:
            col_getter[:, col] = pd.to_datetime(col_getter[:, col]).dt.date
        else:
            col_getter[:, col] = pd.to_datetime(col_getter[:, col])

    return df

def convert_csv_date_columns(input_csv, output_csv, date_columns, remove_time=True, header_rows=0):
    """
    Write a csv file with date columns converted to pd.datetime.
    This is a wrapper for: correct_date_columns_pd()
    Created to facilitate working with SQLite date columns.
    :param input_csv: full directory to the csv file to process.
    :param output_csv: full directory to the revised csv file.
    :param date_columns: an iterable of column names or indexes (integers). Do NOT mix types!
    :param remove_time: removes the time portion of the datetime if True.
    :param header_rows: 'infer' (generally means the first row), list, int or None
    :return: None
    """
    write_header = True if header_rows or header_rows == 0 else False
    print(f"Processing {input_csv} - Time portion removed: {remove_time} - File has header: {write_header}")
    df = correct_date_columns_pd(input_csv=input_csv, date_columns=date_columns, header_rows=header_rows,
                                 remove_time=remove_time)
    df.to_csv(output_csv, index=False, header=write_header)

def csv_parser_model(filepath, gen_func, parser):
    """
    Process data from a csv file. This serves as a model only.
    :param filepath: full directory to the csv file.
    :param gen_func: a generator function that uses csv.Reader or csv.DictReader to yield each line.
    :param parser: a function that parses individual rows yielded from gen_func().
    :return: None
    """
    with open(filepath, 'r', newline='', encoding='utf8') as csv_file:
        for row in gen_func(csv_file):
            data = parser(row)
            yield data

def writer_model(output_csv, input_csv, gen_func, parser):
    """Writes to a csv file using a user-defined parser model. This is an example that currently prints."""
    with open(output_csv, 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        for row in csv_parser_model(input_csv, gen_func=gen_func, parser=parser):
            print(row)


def detect_encoding(filepath):
    """
    Return the file encoding as determined by chardet. 
    You must install chardet: pip install chardet
    The following chardet encodings do work with csv.reader: 'UTF-8-SIG', 'UTF-16', 'ISO-8859-1'
    """
    detector = UniversalDetector()
    for line in open(filepath, 'rb'):
        detector.feed(line)
        if detector.done: 
            break
    detector.close()
    return detector.result.get('encoding')


def main():
    input_csv = './exercise.csv'
    output_csv = './exercise_date_corrected.csv'
    convert_csv_date_columns(input_csv, output_csv, date_columns=[0], remove_time=True, header_rows=0)



if __name__ == '__main__':
    main()
