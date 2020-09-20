#!/usr/bin/env python

from flask import Flask, render_template, request, redirect
import requests
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.embed import components
from werkzeug.exceptions import HTTPException
bv = bokeh.__version__


app = Flask(__name__)
app.vars={}
feat = ['Open','Close','Adj_Open', 'Adj_Close']

@app.route('/')
def main():
	return redirect('/index')


@app.route('/index',methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')
	else:
		#request was a POST
		try:
			app.vars['ticker'] = request.form['ticker'].upper()
			app.vars['select'] = [feat[q] for q in range(4) if feat[q] in request.form.values()]
		except ValueError:
			app.vars['ticker'] = app.vars['ticker'] 
		return redirect('/graph')


@app.route('/graph',methods=['GET','POST'])
def graph():
	
	# Request data from Quandl and get into pandas
	req = 'https://www.quandl.com/api/v3/datasets/WIKI/'
	req = '%s/%s.json?download_type=full&api_key=4Pr7Z6ZryxFmQGPFbRJe' % (req,app.vars['ticker'])
	
	response = requests.get(req)
	
	# run curl command to get column names and output in JSON Format:
	#curl "https://www.quandl.com/api/v3/datasets/WIKI/GOOG/data.json?api_key=4Pr7Z6ZryxFmQGPFbRJe"
	#"Date","Open","High","Low","Close","Volume","Ex-Dividend","Split Ratio","Adj. Open","Adj. High","Adj. Low","Adj. Close","Adj. Volume"
	
	cols = response.json()['dataset']['column_names'][0:14]
	df = pd.DataFrame(np.array(response.json()['dataset']['data'])[:,0:14],columns=cols)
	df.Date = pd.to_datetime(df.Date)
	df[['Open','Close', 'Adj_Open', 'Adj_Close']] = df[['Open','Close', 'Adj. Open', 'Adj. Close']].astype(float)
	app.vars['desc'] = response.json()['dataset']['name'].split(',')[0]
	
	
	# Make Bokeh plot and insert using components
	# ------------------- ------------------------|
	p = figure(plot_width=450, plot_height=450, title=app.vars['ticker'], x_axis_type="datetime")
	if 'Adj_Open' in app.vars['select']:
		line1 = p.line(df.Date, df.Adj_Open, line_width=2,line_color="green",legend_label='Adjusted Opening price')
	if 'Adj_Close' in app.vars['select']:
		line2 = p.line(df.Date, df.Adj_Close, line_width=2,line_color="red",legend_label='Adjusted Closing price')
	if 'Open' in app.vars['select']:
		line3 = p.line(df.Date, df.Open, line_width=2,line_color="blue",legend_label='Opening price')
	if 'Close' in app.vars['select']:
		line4 = p.line(df.Date, df.Close, line_width=2, line_color="yellow",legend_label='Closing price')
	#p.legend.orientation = "vertical"
	
	p.legend.location = 'top_left'
		
	# axis labels
	p.xaxis.axis_label = "Date"
	p.xaxis.axis_label_text_font_style = 'bold'
	p.xaxis.axis_label_text_font_size = '16pt'
	p.xaxis.major_label_orientation = np.pi/4
	p.xaxis.major_label_text_font_size = '14pt'
	p.xaxis.bounds = (df.Date.iloc[-1],df.Date.iloc[0])
	p.yaxis.axis_label = "Price ($)"
	p.yaxis.axis_label_text_font_style = 'bold'
	p.yaxis.axis_label_text_font_size = '16pt'
	p.yaxis.major_label_text_font_size = '12pt'
	
	# render graph template
	# ------------------- ------------------------|
	script, div = components(p)
	return render_template('graph.html', bv=bv, ticker=app.vars['ticker'],
							ttag=app.vars['desc'],
							script=script, div=div)
		
	
@app.errorhandler(500)
def error_handler(e):
	return render_template('error.html',ticker=app.vars['ticker'])

@app.errorhandler(Exception)
def error_handler(e):
	return render_template('error.html',ticker=app.vars['ticker'])
    
# # If main
# -----------------------------------------------------|
if __name__ == '__main__':
  app.run(port=33507,debug=True)