#import libraries

import shiny 
import folium
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import datetime
import altair as alt 
import plotly.express as px
import calendar 
import json
import pathlib
import random
import ipyleaflet as ipyl


from folium.plugins import HeatMap
from ipyleaflet import  Map, Marker, GeoJSON
from shiny import render
from pathlib import Path
from shiny import reactive, App
from shiny.express import input, render, ui, app
from shinywidgets import render_plotly, render_widget, render_altair


from sorted_months_weekdays import * # in order to sort months name
from sort_dataframeby_monthorweek import * # in order to sort months name
from datetime import datetime
from functools import partial
from htmltools import css
from shiny.ui import page_fillable


ui.page_opts(title="Sales Dashboard",fillable=False, id = 'page')


#read file
@reactive.calc
def read_data():
    infile = Path(__file__).parent / "sales.csv"
    df = pd.read_csv(infile)
    df['total_sales'] = df['price_each'] * df['quantity_ordered']
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['hour'] = df['order_date'].dt.hour
    df['month'] = df["order_date"].dt.month_name()
    return df

#sidebar within a card:

with ui.card():
    ui.card_header("Total number of sales by Cities in USA")

    with ui.layout_sidebar():
        with ui.sidebar(bg="#f8f8f8"):

            #first graph selectize
            ui.input_selectize(  
                "city",  
                "Select options below:",  
                ['Dallas (TX)', 'Boston (MA)', 
                'Los Angeles (CA)', 'San Francisco (CA)', 
                'Seattle (WA)', 'Atlanta (GA)', 'New York City (NY)', 
                'Portland (OR)', 'Austin (TX)', 'Portland (ME)'
                ],
                multiple=True,
                selected=['New York City (NY)','Austin (TX)']
            )
            ui.input_dark_mode(mode="light")
        #first graph
        @render.plot
        def plot1():
            df = read_data().copy()
            print(df)
            unique_city = df.city.unique().tolist()
            print(unique_city)
            total_sales_per_city = df.groupby(['city','product'])['total_sales'].sum().reset_index()
            print(total_sales_per_city),
            input_countries = total_sales_per_city[total_sales_per_city['city'].isin(input.city())]
            plt1 = sns.barplot(data=input_countries, 
                                x='city', y = 'total_sales',
                                hue='product')
            plt.gca().set_facecolor('#99CCFF')  # Eksen arka plan rengi
            plt.gcf().set_facecolor('#F0F8FF')  # Grafik figürü arka plan rengi
            plt.legend(loc='upper left',
                    bbox_to_anchor=(1,1),
                    ncol=2,
                    fontsize='small',title='Product Names'
                    )

            return plt1 


#second card
        
with ui.card():
    #tabset w/ tab navigation
    with ui.navset_pill():
        with ui.nav_panel("Most popular ordered product"):
            #Panel A content goes here:
            #second grapd
            @render.plot
            def plot2():
                df2 = read_data().copy()
                print(df2)
                popular_product = df2.groupby('product')[['quantity_ordered','price_each']].sum().reset_index()
                print(popular_product)

                fig, ax1 = plt.subplots(figsize=(10,4))

                #first_plot
                sns.barplot(data=popular_product.sort_values(by='product',ascending=True),x='product'
                        ,y='quantity_ordered', ax=ax1 ,color='g')
                ax1.set_xlabel('Product')
                ax1.set_ylabel('Quantity_Ordered')
                ax1.tick_params(axis='y',labelcolor='g')
                ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90,ha='right')
                    

                #second_plot
                ax2 = ax1.twinx()
                sns.lineplot(data=popular_product.sort_values(by='price_each',ascending=False),x='product'
                      ,y='price_each',ax=ax2, color='b',markers='o')
                ax2.set_ylabel('Price Each',color='b')
                ax2.tick_params(axis='y', labelcolor='r')
                ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90, ha='right')

                plt.tight_layout()
                return fig


        with ui.nav_panel("Total Monthly Sales Numbers"):
                

                #second chart graph selectize:

                ui.input_selectize(
                    "month",
                    "Choose your month here",
                    choices=['January','February','March','April'
                             ,'May','June','July','August','October'
                             ,'November','December'],
                    multiple= True,
                    selected=['January','February','March','April','May']

                )

                @render_plotly
                def plot3():
                    df3 = read_data().copy()
                    grouped = df3.groupby('month')['total_sales'].sum().reset_index()
                    print(grouped)
                    # get the unique month in a list
                    unique_month = df3['month'].unique().tolist()
                    print(unique_month)
                    # sort months in order.
                    sorted_month = Sort_Dataframeby_Month(df = grouped, monthcolumnname='month').replace(' ','')
                    print(sorted_month)
                    months_order = calendar.month_name[1:]
                    #print(months_order)
                    months_sorted = grouped[grouped['month'].isin(input.month())]
                    # create the graph below
                    plt2 = px.bar(months_sorted, x = 'month', y = 'total_sales',
                                 labels='Total Sales Number in Monthly',
                                 category_orders={"month" : months_order})
                    plt.grid()
                                    
                    return plt2
                     
                (ui.input_text_area("textarea","Your Note",placeholder='You can type your notes about the graph in here..',
                                    spellcheck=True))
                
        with ui.nav_panel("Sales Numbers by Hours"):


                @render.plot
                def plot4():
                    df4 = read_data().copy()
                    sales_by_hour = df4['hour'].value_counts().reset_index().sort_values(by = 'hour')
                    print(sales_by_hour)
                    plt.bar(x = sales_by_hour['hour'], height=sales_by_hour['count']
                            ,edgecolor='mediumseagreen',facecolor='C1')
                    plt.xticks(np.arange(0,24))
                    plt.title('Total Sales Number per Hour')
                    plt.ylabel('Sales Numbers')
                    plt.xlabel('Hours')
                    plt.tight_layout()





with ui.card():
    ui.card_header("Sales Number by Cities")


    @render.ui
    def plot4_map():
        df3 = read_data().copy()

        heatmap_data = df3[['lat','long','total_sales']].values
        print(heatmap_data)

        # to create a heat map

        map = folium.Map(location=[35.00, -95.7129], zoom_start=4)
        HeatMap(heatmap_data).add_to(map)

        return map


with ui.navset_card_underline():
    with ui.nav_panel('Sales dataset'):
        @render.data_frame
        def data():
            return render.DataGrid(read_data().head(100),selection_mode="row",filters=True)
            
