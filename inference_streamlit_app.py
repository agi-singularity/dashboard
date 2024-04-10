#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt

#######################
# Page configuration
st.set_page_config(
    page_title="Wand Activities",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
df = pd.read_csv('data/nwu_inference_slim.csv')
#df = df_reshaped

#######################
# Sidebar
with st.sidebar:
    st.title('Wand Activities')
    
    df_action_sorted = df.sort_values(by="action_data", ascending=False)
    df_sorted = df.sort_values(by="activity_id", ascending=True)
    
    activity_list = list(df_sorted.activity_id.unique()) #[::-1]
    selected_activity = st.selectbox('Select Activity', activity_list)
    df_selected_activity = df[df.activity_id == selected_activity]
    df_selected_activity_sorted = df_selected_activity.sort_values(by="action_data", ascending=False)

    action_list = list(df_selected_activity_sorted.action_data.unique())
    selected_action = st.selectbox('Select Action Data', action_list)
    #df_selected_action = df[df.action_data == selected_action]
    df_selected_action = df_selected_activity[df_selected_activity.action_data == selected_action]

    wand_list = list(df_selected_action.wand_identifier.unique())
    selected_wand = st.selectbox('Select Wand', wand_list)
    #df_selected_wand = df_selected_action[df_selected_action.wand_identifier == selected_wand]
    df_selected_wand = df[df.wand_identifier == selected_wand]
    
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference], axis=1).sort_values(by="population_difference", ascending=False)


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Activity Count')

    total_event_count = df.shape[0]
    # total_wand_count = df['Wand Count'].sum()
    # selected_activity_count = df_selected_activity_sorted['Event Count'].sum()
    # #activity_name = df_selected_activity_sorted.activity_id[0]
    
    activity_shape = df_selected_activity.shape
    action_shape = df_selected_action.shape
    wand_shape = df_selected_wand.shape
    
    print(activity_shape, action_shape, wand_shape)
    
    st.metric(label=selected_activity, value=activity_shape[0], delta=None)
    st.metric(label=selected_action, value=action_shape[0], delta=None)
    st.metric(label=selected_wand, value=wand_shape[0], delta=None)
                                                                  
    st.markdown('#### Activity Percentage')

        
    df_activity = round(activity_shape[0]/total_event_count, 4)
    action_activity = round(action_shape[0]/total_event_count, 4)
    wand_activity = round(wand_shape[0]/total_event_count, 4)
    #states_migration_greater = round((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)
    donut_chart_greater = make_donut(df_activity, 'Activity Percentage', 'green')
    donut_chart_less = make_donut(action_activity, 'Action Data Percentage', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Events')
        st.altair_chart(donut_chart_greater)
        st.write('Wands')
        st.altair_chart(donut_chart_less)
        st.write('Wands')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### Unique Wand vs Events')
    
    df1s = df_selected_activity_sorted.groupby(by='action_data').nunique()
    activity_id = df1s['activity_id']
    wand = df1s['wand_identifier']
    action = df1s['action']
    action_data = df1s.index #df1s['action_data']
    session = df1s['session_id']
    # fig, ax = plt.subplots()
    # ax.figure(figsize=(15,10))
    # ax.get_autoscale_on()
    # ax.plot(activity_id, action, label='action')
    # # #plt.plot(activity_id, action_data, label='action_data')
    # ax.plt.bar(activity_id, action_data)
    # ax.tick_params(axis='x', labelcolor='tab:blue', labelrotation=90, labelsize=6)
    # # fig, ax = plt.subplots()
    # st.pyplot(fig)
    
    #heatmap = make_heatmap(df, 'activity_id', 'Wand Count', 'Event Count', selected_color_theme)
    #st.altair_chart(heatmap, use_container_width=True)

    chart_data = df1s #action_data, wand
    
    #st.bar_chart(chart_data)
    #st.scatter_chart(chart_data)
    st.scatter_chart(data=chart_data, width=1000, height=1000, use_container_width=True)

with col[2]:

    import altair as alt
    import streamlit as st
    from vega_datasets import data
    
    source = data.seattle_weather()
    
    scale = alt.Scale(
        domain=["sun", "fog", "drizzle", "rain", "snow"],
        range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
    )
    color = alt.Color("weather:N", scale=scale)
    
    # We create two selections:
    # - a brush that is active on the top panel
    # - a multi-click that is active on the bottom panel
    brush = alt.selection_interval(encodings=["x"])
    click = alt.selection_multi(encodings=["color"])
    
    # Top panel is scatter plot of temperature vs time
    points = (
        alt.Chart()
        .mark_point()
        .encode(
            alt.X("monthdate(date):T", title="Date"),
            alt.Y(
                "temp_max:Q",
                title="Maximum Daily Temperature (C)",
                #scale=alt.Scale(domain=[-5, 40]),
            ),
            color=alt.condition(brush, color, alt.value("lightgray")),
            size=alt.Size("precipitation:Q"), #, scale=alt.Scale(range=[5, 200])),
        )
        .properties(width=550, height=300)
        .add_selection(brush)
        .transform_filter(click)
    )
    
    # Bottom panel is a bar chart of weather type
    bars = (
        alt.Chart()
        .mark_bar()
        .encode(
            x="count()",
            y="weather:N",
            color=alt.condition(click, color, alt.value("lightgray")),
        )
        .transform_filter(brush)
        .properties(
            width=550,
        )
        .add_selection(click)
    )
    
    chart = alt.vconcat(points, bars, data=source, title="Seattle Weather: 2012-2015")
    
    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])
    
    with tab1:
        st.altair_chart(chart, theme="streamlit", use_container_width=True)
    with tab2:
        st.altair_chart(chart, theme=None, use_container_width=True)
   
    st.altair_chart(df1s)
    
    #######################
    source = df_selected_wand
    
    scale = alt.Scale(
        domain=["activity_id", "action", "event_id", "session_id", "headphone_state"],
        range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
    )
    color = alt.Color("activity_id:N", scale=scale)
    
    # We create two selections:
    # - a brush that is active on the top panel
    # - a multi-click that is active on the bottom panel
    brush = alt.selection_interval(encodings=["x"])
    click = alt.selection_multi(encodings=["color"])
    
    # Top panel is scatter plot of temperature vs time
    points = (
        alt.Chart()
        .mark_point()
        .encode(
            alt.X("timestamp:T", title="timestamp"),
            alt.Y(
                "activity_id:Q",
                title="Activity ID",
                #scale=alt.Scale(domain=[-5, 40]),
            ),
            color=alt.condition(brush, color, alt.value("lightgray")),
            size=alt.Size("activity_id:Q") #scale=alt.Scale(range=[5, 200])),
        )
        .properties(width=550, height=300)
        .add_selection(brush)
        .transform_filter(click)
    )
    
    # Bottom panel is a bar chart of weather type
    bars = (
        alt.Chart()
        .mark_bar()
        .encode(
            x="count()",
            y="activity_id",
            color=alt.condition(click, color, alt.value("lightgray")),
        )
        .transform_filter(brush)
        .properties(
            width=550,
        )
        .add_selection(click)
    )
    
    chart = alt.vconcat(points, bars, data=source, title="Action Data")
    
    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])
    
    with tab1:
        st.altair_chart(chart, theme="streamlit", use_container_width=True)
    with tab2:
        st.altair_chart(chart, theme=None, use_container_width=True)
    #from vega_datasets import data
    
    # @st.cache_data
    # def get_data():
    #     source = data.stocks()
    #     source = source[source.date.gt("2004-01-01")]
    #     return source
    
    # source = get_data()
    
    # # Original time series chart. Omitted `get_chart` for clarity
    # chart = get_chart(source)
    
    # Input annotations
    # ANNOTATIONS = [
    #     ("Mar 01, 2008", "Pretty good day for GOOG"),
    #     ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
    #     ("Nov 01, 2008", "Market starts again thanks to..."),
    #     ("Dec 01, 2009", "Small crash for GOOG after..."),
    # ]
    
    # # Create a chart with annotations
    # annotations_df = df1s #pd.DataFrame(ANNOTATIONS, columns=["action_data", "activity_id"])
    # #annotations_df.date = pd.to_datetime(annotations_df.date)
    # annotations_df["y"] = 0
    # annotation_layer = (
    #     alt.Chart(annotations_df)
    #     .mark_text(size=5, text="⬇", dx=0, dy=-10, align="center")
    #     .encode(
    #         x="action_data:T",
    #         y=alt.Y("y:Q"),
    #         tooltip=["action_data"],
    #     )
    #     .interactive()
    # )
    
    # # Display both charts together
    # st.altair_chart((annotation_layer), use_container_width=True)

#     st.markdown('#### Top Activities')

#     st.dataframe(df_selected_activity_sorted,
#                  column_order=("action_data", "Wand Count", "Event Count"),
#                  hide_index=True,
#                  width=None,
#                  column_config={
#                     "Activity": st.column_config.TextColumn(
#                         "activity_id",
#                     ),
#                     "Wand": st.column_config.ProgressColumn(
#                         "Wand Count",
#                         format="%f",
#                         min_value=0,
#                         max_value=max(df['activity_id']),
#                      )}
#                  )
    
   
