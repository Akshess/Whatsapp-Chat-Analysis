import streamlit as st
import pandas as pd
import re


# Preprocessing
def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    # pass the pattern and data to split it to get the list of messages
    messages = re.split(pattern, data)[1:]
    # extract all dates
    dates = re.findall(pattern, data)

    # create dataframe
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M  - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract multiple columns from the Date Column
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period
    return df


# Funtion to fetch Stats
def helper_fetch(selected_user, df):
    if selected_user == 'Overall':
        words = []
        for message in df['message']:
            words.extend(message.split())
        return df.shape[0], len(words)
    else:
        words = []
        new_df = df[df['user'] == selected_user]
        for message in new_df['message']:
            words.extend(message.split())
        return new_df.shape[0], len(words)


# Streamlit
st.sidebar.title('Whatsapp Chat Analyser')
upload = st.sidebar.file_uploader('Choose File')
if upload is not None:
    bytes_data = upload.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocess(data)

    st.dataframe(df)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox('Show analysis wrt', user_list)
    if st.sidebar.button('Run Analysis'):
        num_messages,words = helper_fetch(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.header("Total Messages")
            st.subheader(num_messages)
        with col2:
            st.header("Total Words")
            st.subheader(words)
