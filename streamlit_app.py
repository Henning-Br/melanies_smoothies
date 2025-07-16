# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title( f" :cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

import streamlit as st
from snowflake.snowpark.functions import col

name_on_ordner = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_ordner)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOL function
pd_df=my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)
  
st.dataframe(pd_df)
#st.stop()


if ingredients_list:
  
    ingredients_string = ''

   for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '
    
    search_on_series = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
  
    if not search_on_series.empty and pd.notna(search_on_series.iloc[0]):
        search_on = search_on_series.iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')

        smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Fehler beim Abrufen der Daten für {fruit_chosen} (Status Code: {smoothiefroot_response.status_code})")
    else:
        st.warning(f"Kein gültiger 'SEARCH_ON'-Wert für {fruit_chosen} gefunden. Diese Frucht wird übersprungen.")

              # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

      
           # st.subheader(fruit_chosen + 'Nutrition_Information')
           # smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
          # sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    #st.write(ingredients_string)

     
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_ordner+ """')"""

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
     
        st.success('Your Smoothie is ordered!', icon="✅")
