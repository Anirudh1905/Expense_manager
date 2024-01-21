import streamlit as st
import pandas as pd
import plotly.express as px
from babel.numbers import format_currency
import logging
from expense_utils import get_dataframes

# from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="Expense Manager App", layout="wide")
header = st.container()
data = st.container()
viz = st.container()


def get_tag(df, tag, transaction_type):
    new_df = (
        df.groupby([tag]).agg({transaction_type: sum}).sort_values(by=transaction_type, ascending=False)
    )
    new_df.reset_index(inplace=True)
    return new_df


with header:
    st.title("Expense Manager")

with data:
    # username = st.text_input('Enter username')
    uploaded_file = st.file_uploader("Upload your bank statement here (Only CSV)")
    months = [
        "All",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    option = st.selectbox("Enter month for which u want ot see the analysis", months, 0)
    month_idx = months.index(option)
    flag = False
    if uploaded_file is not None and uploaded_file.name[-3:] != "csv":
        st.write("File Format not supported! Please upload CSV file")
        uploaded_file = None

    if uploaded_file is not None:
        flag = True
        df, df_debit, df_credit, df_sum = get_dataframes(
            pd.read_csv(uploaded_file), month_idx
        )
        if len(df) == 0:
            st.write("Sorry! No data found for the current month")
            flag = False
        category_debit = get_tag(df_debit, "category", "debit")
        category_credit = get_tag(df_credit, "category", "credit")
        sub_category_debit = get_tag(df_debit, "sub_category", "debit")
        sub_category_credit = get_tag(df_credit, "sub_category", "credit")
        type_debit = get_tag(df_debit, "type", "debit")
        type_credit = get_tag(df_credit, "type", "credit")
        df_debit["transaction_type"] = ["debit"] * len(df_debit)
        df_credit["transaction_type"] = ["credit"] * len(df_credit)
        df_debit.rename(columns={"debit": "amount"}, inplace=True)
        df_credit.rename(columns={"credit": "amount"}, inplace=True)
        amount_df = pd.concat(
            [
                df_debit[
                    ["date", "amount", "transaction_type", "category", "sub_category", "month"]
                ],
                df_credit[
                    ["date", "amount", "transaction_type", "category", "sub_category", "month"]
                ],
            ]
        )
        amount_df = amount_df.sort_values(by="date").reset_index(drop=True)

        csv_file = df.to_csv(index=False)
        st.download_button(
            label="Download Output CSV",
            data=csv_file,
            file_name="expense_output.csv",
            key="csv_button",
        )

with viz:
    if flag:
        st.header("Data Visualizations")
        st.subheader(
            "Total Debit: "
            + str(format_currency(df_sum.loc[0, "Sum"], "INR", locale="en_IN"))
        )
        st.subheader(
            "Total Credit: "
            + str(format_currency(df_sum.loc[1, "Sum"], "INR", locale="en_IN"))
        )
        fig = px.line(
            amount_df,
            x="date",
            y="amount",
            color="transaction_type",
            title="Transaction type wise Debit",
            labels={"date": "Date"},
            custom_data=[amount_df["category"], amount_df["sub_category"]],
            color_discrete_map={"credit": "green", "debit": "red"}
        )
        hovertemp = "<b>Date: </b> %{x} <br>"
        hovertemp += "<b>Amount: </b> %{y} <br>"
        hovertemp += "<b>Category: </b> %{customdata[0]} <br>"
        hovertemp += "<b>Sub Category: </b> %{customdata[1]}"
        fig.update_traces(hovertemplate=hovertemp)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        # fig = px.pie(df_sum,values='Sum',names='index',title="Debit vs Credit")
        # fig.update_layout(title_x=0.43)
        # st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        fig = px.bar(
            amount_df,
            x="month",
            y="amount",
            color="transaction_type",
            title="Month wise Transaction",
            labels={"month": "Month"},
            barmode="group",
            custom_data=[amount_df["category"], amount_df["sub_category"]],
            color_discrete_map={"credit": "blue", "debit": "orange"}
        )
        fig.update_traces(hovertemplate=hovertemp)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        left, right = st.columns(2)
        fig_l = px.pie(
            category_debit, values="debit", names="category", title="Categorywise Debit"
        )
        left.plotly_chart(fig_l, theme="streamlit", use_container_width=True)

        fig_l = px.pie(
            sub_category_debit,
            values="debit",
            names="sub_category",
            title="Sub Categorywise Debit",
        )
        left.plotly_chart(fig_l, theme="streamlit", use_container_width=True)

        fig_l = px.pie(
            type_debit,
            values="debit",
            names="type",
            title="Transaction type wise Debit",
        )
        left.plotly_chart(fig_l, theme="streamlit", use_container_width=True)

        fig_r = px.pie(
            category_credit,
            values="credit",
            names="category",
            title="Categorywise Credit",
        )
        right.plotly_chart(fig_r, theme="streamlit", use_container_width=True)

        fig_r = px.pie(
            sub_category_credit,
            values="credit",
            names="sub_category",
            title="Sub Categorywise Credit",
        )
        right.plotly_chart(fig_r, theme="streamlit", use_container_width=True)

        fig_r = px.pie(
            type_credit,
            values="credit",
            names="type",
            title="Transaction type wise Credit",
        )
        right.plotly_chart(fig_r, theme="streamlit", use_container_width=True)
