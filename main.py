import os
import csv
import json
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import boto3


CSV_FILE = "가계부.csv"
TABS = ["추가", "수정", "삭제"]
EXPENSE_CATEGORIES = ["식품", "주거", "교통", "의류", "건강", "여가", "교육", "통신", "가정", "기타"]


def main():
    entries = read_entries()

    st.title("가계부")
    show_category_statistics(entries)
    tab1, tab2, tab3 = st.tabs(TABS)
    with tab1:
        add_entry(entries)
    with tab2:
        update_entry(entries)
    with tab3:
        delete_entry(entries)
    show_entries(entries)


def show_entries(entries):
    df = pd.DataFrame.from_dict(
        entries, orient="index", columns=["날짜", "카테고리", "내용", "금액", "메모"]
    )
    st.table(df)


def add_entry(entries):
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        date = st.date_input("날짜를 입력하세요:")
    with col2:
        category = st.multiselect(
            "카테고리를 입력하세요:", EXPENSE_CATEGORIES, default=[], max_selections=1
        )
    with col3:
        description = st.text_input("내용을 입력하세요:")
    with col4:
        amount = st.text_input("금액을 입력하세요:")
    memo = st.text_input("메모를 입력하세요:")

    if st.button("추가"):
        if not entries:
            entry_id = 1
        else:
            entry_id = max(map(int, entries.keys())) + 1
        entries[entry_id] = [date, category[0], description, amount, memo]
        write_entries(entries)
        st.success("가계 내역을 추가했어요.")


def update_entry(entries):
    entry_id = st.number_input(
        "수정할 가계 내역의 ID를 입력하세요:", format="%d", step=1, min_value=0
    )
    if entry_id not in entries:
        st.warning("ID에 해당하는 가계 내역이 없어요.")
        return

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        date = st.date_input(
            "수정된 날짜를 입력하세요:", datetime.strptime(entries[entry_id][0], "%Y-%m-%d")
        )
    with col2:
        category = st.multiselect(
            "수정된 카테고리를 입력하세요:",
            EXPENSE_CATEGORIES,
            default=[entries[entry_id][1]],
            max_selections=1,
        )
    with col3:
        description = st.text_input("수정된 내용을 입력하세요:", entries[entry_id][2])
    with col4:
        amount = st.text_input("수정된 금액을 입력하세요:", entries[entry_id][3])
    memo = st.text_input("수정된 메모를 입력하세요:", entries[entry_id][4])

    if st.button("수정"):
        entries[entry_id] = [date, category[0], description, amount, memo]
        write_entries(entries)
        st.success("가계 내역을 수정했어요.")


def delete_entry(entries):
    entry_id = st.number_input(
        "삭제할 가계 내역의 ID를 입력하세요:", format="%d", step=1, min_value=0
    )
    if entry_id not in entries:
        st.warning("ID에 해당하는 가계 내역이 없어요.")
        return

    if st.button("삭제"):
        del entries[entry_id]
        write_entries(entries)
        st.success("가계 내역을 삭제했어요.")


def show_category_statistics(entries):
    categories = {}
    for entry in entries.items():
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
        st.warning("가계 내역이 없어요.")

    if st.button("차트 업데이트"):
        st.experimental_rerun()


def create_file(file_name, file_contents):
    lambda_client = boto3.client("lambda")
    lambda_client.invoke(
        FunctionName="wontory-ICN-create-file",
        InvocationType="RequestResponse",
        Payload=json.dumps({"file_name": file_name, "file_contents": file_contents}),
    )

    return True


def read_file(file_name):
    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName="wontory-ICN-read-file",
        InvocationType="RequestResponse",
        Payload=json.dumps({"file_name": file_name}),
    )

    payload = json.loads(response["Payload"].read())

    file_contents = payload.get("file_contents")

    return file_contents


def read_entries():
    entries = {}

    file_contents = read_file(CSV_FILE)

    contents = file_contents.split("\n")
    contents = list(filter(None, contents))
    contents_list = [content.split(", ") for content in contents]

    for row in contents_list:
        entry_id = int(row[0])
        entry = row[1:]
        entries[entry_id] = entry

    return entries


def write_entries(entries):
    file_contents = ""
    for entry_id, entry in entries.items():
        str_entry = list(map(str, [entry_id] + entry))
        file_contents += ", ".join(str_entry) + "\n"

    create_file(CSV_FILE, file_contents)


if __name__ == "__main__":
    main()
