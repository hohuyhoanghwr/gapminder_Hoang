import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def preprocessing(file):
    df = pd.read_csv(file)
    df_melted = df.melt(id_vars="country", var_name="year", value_name=f"{file.removesuffix('.csv')}")
    df_melted.loc[:,"year"] = df_melted["year"].astype(int)
    df_melted = df_melted.sort_values(by=["country", "year"])
    df_melted.loc[:,f"{file.removesuffix('.csv')}"] = df_melted.groupby("country",group_keys=False)[f"{file.removesuffix('.csv')}"].ffill().bfill()
    df_melted.reset_index(drop=True, inplace=True)
    return df_melted

@st.cache_data(ttl=3600)
def load_data():    
    lex = preprocessing("lex.csv")
    ny_gnp_pcap_pp_cd = preprocessing("ny_gnp_pcap_pp_cd.csv")
    pop = preprocessing("pop.csv")
    df = pd.merge(lex, ny_gnp_pcap_pp_cd, on=["country", "year"], how="outer")
    df = pd.merge(df, pop, on=["country", "year"], how="outer")
    print(df)    
    return df

# Load and cache the merged data
df = load_data()
import plotly.express as px
st.title('Gapminder')
st.write("BIPM project - Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication ")

# Year slider with play button
year = st.slider("Select year", min_value=int(df["year"].min()), max_value=int(df["year"].max()), step=1)

# Country multi-select
all_countries = df["country"].unique().tolist()
selected_countries = st.multiselect("Select countries", all_countries, default=["Germany", "USA", "Vietnam"])

# Filtered DataFrame
filtered_df = df[(df["year"] == year) & (df["country"].isin(selected_countries))]

# Convert GNI per capita and pop to numeric (in case they were strings like "12.3k" or "1.2M")
def parse_number(val):
    if isinstance(val, str):
        val = val.replace('k', 'e3').replace('M', 'e6')
    return pd.to_numeric(val, errors='coerce')

filtered_df["ny_gnp_pcap_pp_cd"] = filtered_df["ny_gnp_pcap_pp_cd"].apply(parse_number)
filtered_df["pop"] = filtered_df["pop"].apply(parse_number)

# Plotly bubble chart
fig = px.scatter(
    filtered_df,
    x="ny_gnp_pcap_pp_cd",
    y="lex",
    size="pop",
    color="country",
    log_x=False,
    size_max=60,
    labels={
        "ny_gnp_pcap_pp_cd": "GNI per Capita",
        "lex": "Life Expectancy",
        "pop": "Population"
    },
    title=f"Year {year}"
)

st.plotly_chart(fig)