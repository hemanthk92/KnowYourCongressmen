from flask import Flask, request, render_template
app = Flask(__name__)
import pandas as pd 
from mat_gen import Voting_Matrix 
from scipy.spatial.distance import pdist, squareform, cosine
import numpy as np
from bokeh.plotting import figure, gridplot, output_file, show
import us
from bokeh.io import output_notebook, show, output_file
from bokeh.models import HoverTool, CrosshairTool
from bokeh.plotting import *
from scipy.stats import mode 
from bokeh.embed import autoload_static
import random

# home page
@app.route('/')
def index():
	'''
	Home page
	'''
	return render_template('index.html')

@app.route('/graph', methods=['POST'] )

def graph():
	'''
	Code for Graph that loads the correspoding text file with the ditances and graphs it. 
	'''
	category_map = {'Health Care': [1], 'National Security': [2], 'Economy': [3], \
					'Environment': [4], 'Domestic Issues': [5], 'All Categories': [0,1,2,3,4,5]} 
	category = str(request.form['category'])
	category_value = category_map[category]
	selected_member = str(request.form['person']) 
	df_members = pd.read_csv('../DataCollectionInsertion/Members/114Members.csv')
	row = df_members[df_members['person__name'] == selected_member]['row_nums'].iloc[0]

	democrats = [(df_members.iloc[i]['person__id'], df_members.iloc[i]['row_nums'], df_members.iloc[i]['person__name']) \
				for i in xrange(len(df_members)) if df_members.iloc[i]['party'] == 'Democrat' if df_members.iloc[i]['row_nums'] != row]
	republicans = [(df_members.iloc[i]['person__id'], df_members.iloc[i]['row_nums'], df_members.iloc[i]['person__name']) \
				for i in xrange(len(df_members)) if df_members.iloc[i]['party'] == 'Republican' if df_members.iloc[i]['row_nums'] != row]
	
	democrats_rows = [democrat[1] for democrat in democrats]
	republicans_rows = [republican[1] for republican in republicans]
	democrats_names = [democrat[2] for democrat in democrats]
	republicans_names = [republican[2] for republican in republicans]

	distances = np.loadtxt('../CosineSimilarity/data/' + category + '114Distance.csv', delimiter=',')

	member_title = selected_member

	source1 = ColumnDataSource(\
				data=dict(x=range(0, len(republicans_rows)), y= list(distances[row, republicans_rows]), \
				label= republicans_names))

	source2 = ColumnDataSource(\
				data=dict(x=range(0, len(democrats_rows)), y= list(distances[row, democrats_rows]), \
				label= democrats_names))

	source3 = ColumnDataSource(data=dict(x=[125], y=[0.0], label= [selected_member]))

	hover = HoverTool(
		tooltips=[
			("Distance", "@y"),
			("Name","@label"),
		]
	)

	TOOLS = [hover, CrosshairTool()]

	title = '%s \t %s' %(category, member_title)

	p = figure(title = title, plot_width=600, plot_height=600, \
	                                y_axis_label = 'Distance', tools = TOOLS)

	random.sample(range(1, len(republicans_rows)), len(democrats_rows)),
	
	p.circle(x = [i*len(republicans_rows)/len(democrats_rows) for i in xrange(len(democrats_rows))],  y = distances[row, democrats_rows],\
			source = source2, size = 6, color = '#0000FF')

	p.circle(x = range(0, len(republicans_rows)), y = distances[row, republicans_rows],\
			source=source1, size = 6, color = '#FF0000')
	p.x(125, 0, size = 15, color = '#008000', source = source3)
	
	p.title_text_color = "olive"
	p.title_text_font = "times"
	p.title_text_font_style = "italic"
	p.background_fill = "beige"
	p.xaxis.visible = None
	
	save(p, "/Users/HemanthKondapalli/KnowYourCongressMen/WebSite/templates/fig.html")
	
	return render_template('graph.html') 

@app.route('/predict', methods=['POST'] )

def predict():
	'''
	Loading predicted values for missing votes and displaying the table as html 
	'''
	person_name = str(request.form['person_predict'])
	df_pred = pd.read_csv('data/nmf_114predictions.csv')

	df_members = pd.read_csv('../DataCollectionInsertion/Members/114Members.csv')
	member_id = df_members[df_members['person__name'] == person_name]['person__id'].iloc[0]
	
	missing_votes = df_pred[df_pred['Member'] == member_id][['Bill', 'Link', 'Vote', 'Question']]
	pd.set_option('display.max_colwidth', -1)

	link_strings=[]
	for i in xrange(len(missing_votes)):
		text =  missing_votes.iloc[i]['Question']
		link = missing_votes.iloc[i]['Link']
		link_strings.append('<a href=' + '"'+ link +'"'+ '>' + text + '</a>')

	missing_votes['Question'] = link_strings
	missing_votes[['Bill', 'Question', 'Vote']].to_html('templates/table.html', col_space = 1000, escape = False, index = False, max_rows = 100, justify='left')
	
	return render_template('predict.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)