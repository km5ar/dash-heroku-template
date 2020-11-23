import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
#from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


#%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])



mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')



markdown_text= '''
Gender Wage Gap

According to the 2018 Census Bureau, women's median income is 82% of that for men, which means there is an 18% potential gender wage gap. However, there may also be other external factors besides gender. Amongst the reasons for the differences in pay between genders are differences in industries, education, etc. We wish to explore the differences in pay by gender, while controlling for other factors, in order to get a more acute view of the wage gap in context. (Reference: https://www.americanprogress.org/issues/women/reports/2020/03/24/482141/quick-facts-gender-wage-gap/)


GSS

The General Social Survey collects data from Americans on different demographic information, sentiments, and behaviors to track trends over time. The survey has data recorded from 1972. We decided to use the General Social Survey in the following dashboard to compare different attributes, such as occupational prestige and income, for both men and women. (Reference: http://www.gss.norc.org/About-The-GSS)
'''



gss_bar = gss_clean.groupby('sex', sort=False).agg({'income':'mean',
                                     'job_prestige':'mean',
                                    'socioeconomic_index':'mean',
                                             'education':'mean'})

gss_bar['income'] = round(gss_bar['income'],2)

gss_bar['job_prestige'] = round(gss_bar['job_prestige'],2)

gss_bar['socioeconomic_index'] = round(gss_bar['socioeconomic_index'],2)

gss_bar['education'] = round(gss_bar['education'],2)

gss_bar = gss_bar.reset_index().rename({'sex':'Sex','income': 'Mean Income', 
                                        'job_prestige': 'Mean Occupational Prestige', 
                                        'socioeconomic_index': 'Mean Socioeconomic Index', 
                                        'education': 'Mean Education Level' }, axis=1)

#gss_bar # basical version


# web enable version of this table
table = ff.create_table(gss_bar)
#table.show()



gss_bw_group = gss_clean.groupby(['sex', 'male_breadwinner'], sort=False)#.size()
gss_bw = gss_bw_group.size().reset_index() 
#gss_bw


gss_bar=px.bar(gss_bw, x='male_breadwinner', y=0, 
               color='sex', 
               barmode='group', 
               labels={'0':'Count', 'male_breadwinner':'Level of Agreement'})
#gss_bar

gss_scatter = gss_clean[~gss_clean.sex.isnull()] # exclus null number in gss_clean sex column

#'lowess'
fig_scatter = px.scatter(gss_scatter.head(200), 
                         x='job_prestige', 
                         y='income', 
                         trendline='ols',
                 color = 'sex', 
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income'},
                 hover_data=['sex', 
                             'education', 
                             'socioeconomic_index'])
fig_scatter.update(layout=dict(title=dict(x=0.5)))
#fig_scatter.show()

fig_box = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Income', 'sex':''}, )
fig_box.update_layout(showlegend=False)
#fig_box.show()


fig_box2 = px.box(gss_clean, 
                  x='job_prestige', 
                  y = 'sex', 
                  color = 'sex',
                   labels={'job_prestige':'Occupational Prestige', 'sex':''})
fig_box2.update_layout(showlegend=False)
#fig_box2.show()


gss_facet= gss_clean[['income', 'sex', 'job_prestige']]  # subset the data 
#gss_facet

gss_facet['job_prestige_cat'] = pd.cut(gss_facet.job_prestige, 
                                       bins=[15,26,37,48,59,70,81], 
                                       labels=("16-26","27-37", "38-48", "49-59","60-70","71-81"))


gss_facet=gss_facet.dropna() # drop all rows with any missing values in this dataframe
#gss_facet


fig_facet = px.box(gss_facet, 
                   x='income', 
                   y='sex', 
                   color='sex', 
             facet_col='job_prestige_cat', 
                   facet_col_wrap=2,
            labels={'income':'Income', 
                    'sex':''})
fig_facet.update(layout=dict(title=dict(x=0.5)))
#fig_facet.show()


#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div(
    [
        html.H1("Exploring the 2019 General Social Survey: Differences in Sexes"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H4("Table Comparing Mean Income, Occupational Prestige, Socioeconomic Index and Education Level between Men and Women"),
        
        dcc.Graph(figure=table),
        
        html.H4("Barplot Comparing Level of Agreement with the Idea that Males are Breadwinners, between Men and Women"),
        
        dcc.Graph(figure=gss_bar),
        
        html.H4("Scatterplot Comparing Occupational Prestige and Income between Men and Women"),
        
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            
            html.H5("Boxplot Comparing Income between Men and Women"),
            
            dcc.Graph(figure=fig_box)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H5("Boxplot Comparing Occupational Prestige between Men and Women"),
            
            dcc.Graph(figure=fig_box2)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H4("Boxplots Comparing Income between Men and Women for Occupational Prestige Categories"),
        
        dcc.Graph(figure=fig_facet)
    
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True) # different number  # , use_reloader=False
    #app.run_server(mode='inline', debug=True, port=8050) #  port = 8001,
    
