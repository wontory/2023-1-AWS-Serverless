import csv
import os
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import logging
import boto3
from botocore.exceptions import ClientError
import os


CSV_FILE = '가계부.csv'
TABS = ["추가", "수정", "삭제"]
EXPENSE_CATEGORIES = ['식품', '주거', '교통', '의류', '건강', '여가', '교육', '통신', '가정', '기타']


def main():
    st.title('가계부')
    show_category_statistics()
    tab1, tab2, tab3 = st.tabs(TABS)
    with tab1:
        add_entry()
    with tab2:
        update_entry()
    with tab3:
        delete_entry()
    show_entries()


def show_entries():
    if not os.path.exists(CSV_FILE):
        st.warning('가계부 파일이 존재하지 않아요.')
        return

    entries = read_entries()
    df = pd.DataFrame.from_dict(entries, orient='index', columns=['날짜', '카테고리', '내용', '금액', '메모'])
    st.table(df)


def add_entry():
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        date = st.date_input('날짜를 입력하세요:')
    with col2:
        category = st.multiselect('카테고리를 입력하세요:', EXPENSE_CATEGORIES, default=[], max_selections=1)
    with col3:
        description = st.text_input('내용을 입력하세요:')
    with col4:
        amount = st.text_input('금액을 입력하세요:')
    memo = st.text_input('메모를 입력하세요:')

    if st.button('추가'):
        entries = read_entries()
        if not entries:
            entry_id = 1
        else:
            entry_id = max(map(int, entries.keys())) + 1
        entries[entry_id] = [date, category[0], description, amount, memo]
        write_entries(entries)
        st.success('가계 내역을 추가했어요.')


def update_entry():
    entry_id = st.number_input('수정할 가계 내역의 ID를 입력하세요:', format="%d", step=1, min_value=0)
    entries = read_entries()
    if entry_id not in entries:
        st.warning('ID에 해당하는 가계 내역이 없어요.')
        return

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        date = st.date_input('수정된 날짜를 입력하세요:', datetime.strptime(entries[entry_id][0], '%Y-%m-%d'))
    with col2:
        category = st.multiselect('수정된 카테고리를 입력하세요:', EXPENSE_CATEGORIES, default=[entries[entry_id][1]], max_selections=1)
    with col3:
        description = st.text_input('수정된 내용을 입력하세요:', entries[entry_id][2])
    with col4:
        amount = st.text_input('수정된 금액을 입력하세요:', entries[entry_id][3])
    memo = st.text_input('수정된 메모를 입력하세요:', entries[entry_id][4])

    if st.button('수정'):
        entries[entry_id] = [date, category[0], description, amount, memo]
        write_entries(entries)
        st.success('가계 내역을 수정했어요.')


def delete_entry():
    entry_id = st.number_input('삭제할 가계 내역의 ID를 입력하세요:', format="%d", step=1, min_value=0)
    entries = read_entries()
    if entry_id not in entries:
        st.warning('ID에 해당하는 가계 내역이 없어요.')
        return

    if st.button('삭제'):
        del entries[entry_id]
        write_entries(entries)
        st.success('가계 내역을 삭제했어요.')


def show_category_statistics():
    categories = {}
    entries = read_entries()
    for entry_id, entry in entries.items():
        category = entry[1]
        amount = float(entry[3])
        if category in categories:
            categories[category] += amount
        else:
            categories[category] = amount

    if categories:
        labels = list(categories.keys())
        values = list(categories.values())
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        st.plotly_chart(fig)
    else:
        st.warning('가계 내역이 없어요.')

    if st.button('차트 업데이트'):
        st.experimental_rerun()


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def read_entries():
    entries = {}

    if not os.path.exists(CSV_FILE):
        return entries

    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            entry_id = int(row[0])
            entry = row[1:]
            entries[entry_id] = entry

    return entries


def write_entries(entries):
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for entry_id, entry in entries.items():
            writer.writerow([entry_id] + entry)
    upload_file('가계부.csv', 'cdk-hnb659fds-assets-909857918710-ap-northeast-2', '가계부.csv')


if __name__ == '__main__':
    main()
