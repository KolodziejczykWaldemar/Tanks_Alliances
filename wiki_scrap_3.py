import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def repair_row(row):
    if len(row) <= 2:
        return None
    result = []
    for word in row:
        if not word == '\n':
            formatted = word.replace('\xa0', '')
            formatted = formatted.replace(',', '')
            formatted = formatted.replace('\n', '')
            if '[' in word:
                for i in range(len(formatted)):
                    if formatted[i] == '[':
                        result.append(formatted[:i])
                        break
            else:
                result.append(formatted)

    return result


def delete_none(list):
    ready = []
    for elem in list:
        if elem:
            ready.append(elem)

    return ready


def remove_parents(word):
    if ' [' in word or ' (' in word:
        for i in range(len(word)):
            if word[i] == '[' or word[i] == '(':
                return word[:i-1]
    if '[' in word or '(' in word:
        for i in range(len(word)):
            if word[i] == '[' or word[i] == '(':
                return word[:i]
    else:
        return word

url = 'https://en.wikipedia.org/wiki/List_of_main_battle_tanks_by_country?fbclid=IwAR1AmFmhWQZkZpRXe5AR25kziP_Or_adLL_B75g1drj-UTKJNlNuqy5XyKs'
response = requests.get(url)
soup = BeautifulSoup(response.text)

tables = soup.findAll("table", {"class": "wikitable"})
"""
rows = tables[0].find_all('tr')


all_rows = []
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        vals = []
        for x in row.find_all('td'):
            vals.append(x.get_text())
            print(x.rowspan)
        all_rows.append(repair_row(vals))

print(all_rows)
repaired_rows = delete_none(all_rows)
"""


def pre_process_table(table):
    """
    INPUT:
        1. table - a bs4 element that contains the desired table: ie <table> ... </table>
    OUTPUT:
        a tuple of:
            1. rows - a list of table rows ie: list of <tr>...</tr> elements
            2. num_rows - number of rows in the table
            3. num_cols - number of columns in the table
    Options:
        include_td_head_count - whether to use only th or th and td to count number of columns (default: False)
    """
    rows = [x for x in table.find_all('tr')]

    num_rows = len(rows)

    # get an initial column count. Most often, this will be accurate
    num_cols = max([len(x.find_all(['th','td'])) for x in rows])

    # sometimes, the tables also contain multi-colspan headers. This accounts for that:
    header_rows_set = [x.find_all(['th', 'td']) for x in rows if len(x.find_all(['th', 'td']))>num_cols/2]

    num_cols_set = []

    for header_rows in header_rows_set:
        num_cols = 0
        for cell in header_rows:
            row_span, col_span = get_spans(cell)
            num_cols += len([cell.getText()]*col_span)

        num_cols_set.append(num_cols)

    num_cols = max(num_cols_set)

    return (rows, num_rows, num_cols)


def get_spans(cell):
        """
        INPUT:
            1. cell - a <td>...</td> or <th>...</th> element that contains a table cell entry
        OUTPUT:
            1. a tuple with the cell's row and col spans
        """
        if cell.has_attr('rowspan'):
            rep_row = int(cell.attrs['rowspan'])
        else:  # ~cell.has_attr('rowspan'):
            rep_row = 1
        if cell.has_attr('colspan'):
            rep_col = int(cell.attrs['colspan'])
        else:  # ~cell.has_attr('colspan'):
            rep_col = 1

        return (rep_row, rep_col)

def process_rows(rows, num_rows, num_cols):
    """
    INPUT:
        1. rows - a list of table rows ie <tr>...</tr> elements
    OUTPUT:
        1. data - a Pandas dataframe with the html data in it
    """
    data = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
    for i, row in enumerate(rows):
        try:
            col_stat = data.iloc[i,:][data.iloc[i,:].isnull()].index[0]
        except IndexError:
            print(i, row)

        for j, cell in enumerate(row.find_all(['td', 'th'])):
            rep_row, rep_col = get_spans(cell)

            while any(data.iloc[i,col_stat:col_stat+rep_col].notnull()):
                col_stat += 1

            data.iloc[i:i+rep_row, col_stat:col_stat+rep_col] = cell.getText()
            if col_stat < data.shape[1]-1:
                col_stat += rep_col

    return data


rows, num_rows, num_cols = pre_process_table(tables[0])
df = process_rows(rows[1:], num_rows-1, num_cols)
for table in tables[1:]:
    rows2, num_rows2, num_cols2 = pre_process_table(table)
    df2 = process_rows(rows2[1:], num_rows2-1, num_cols2)
    df = df.append(df2, ignore_index=True)


df = df.drop(df.columns[4], axis=1)

indexNames = df[df[1] == df[2]].index
df.drop(indexNames, inplace=True)

df = df[df[2].notnull()]
df = df[df[3].notnull()]

vals = df.values
arr = []
for row in vals:
    row_new = []
    for cell in row:
        cell_repaired = cell.replace('\n', '')
        cell_repaired = cell_repaired.replace('\xa0', '')
        cell_repaired = cell_repaired.replace('Soviet Union', 'Russia')
        cell_repaired = cell_repaired.replace('USSR', 'Russia')
        cell_repaired = cell_repaired.replace('Korea, North', 'North Korea')
        cell_repaired = cell_repaired.replace('Korea, South', 'South Korea')
        cell_repaired = cell_repaired.replace('United States', 'United States of America')
        cell_repaired = cell_repaired.replace('Republic of China', 'China')
        cell_repaired = cell_repaired.replace('Congo, Democratic Republic of', 'Congo')
        cell_repaired = cell_repaired.replace('Congo, Republic of', 'Congo')
        if 'Russia' in cell_repaired:
            row_new.append('Russia')
        else:
            row_new.append(remove_parents(cell_repaired))
    arr.append(row_new)
df_no_parents = pd.DataFrame(np.asarray(arr))


names_repaired = []
for row in df_no_parents.values:
    if '/' in row[3]:
        for i in range(len(row[3])):
            if row[3][i] == '/':
                if row[3][i-1] == ' ':
                    split1 = [row[0], row[1], row[2], row[3][:i-1]]
                    split2 = [row[0], row[1], row[2], row[3][i + 1:]]
                    names_repaired.append(split1)
                    names_repaired.append(split2)
                    break
                if row[3][i + 1] == ' ':
                    split1 = [row[0], row[1], row[2], row[3][:i]]
                    split2 = [row[0], row[1], row[2], row[3][i + 2:]]
                    names_repaired.append(split1)
                    names_repaired.append(split2)
                    break
                if row[3][i-1] == ' ' and row[3][i + 1] == ' ':
                    split1 = [row[0], row[1], row[2], row[3][:i - 1]]
                    split2 = [row[0], row[1], row[2], row[3][i + 2:]]
                    names_repaired.append(split1)
                    names_repaired.append(split2)
                    break
                else:
                    split1 = [row[0], row[1], row[2], row[3][:i]]
                    split2 = [row[0], row[1], row[2], row[3][i + 1:]]
                    names_repaired.append(split1)
                    names_repaired.append(split2)
    else:
        names_repaired.append(row)

df_ready = pd.DataFrame(np.asarray(names_repaired))


print(df_ready)
df_ready.to_csv('tanks.csv')
unique_names = []
unique_names.append(df_ready[0].unique().tolist())
unique_names.append(df_ready[3].unique().tolist())
print(len(df_ready[0].unique()))

names_repaired = []


uniques = []
for m in unique_names:
    for n in m:
        uniques.append(n)
print(len(uniques))
uniques_set = set(uniques)
print(list(uniques_set))