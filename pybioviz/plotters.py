#!/usr/bin/env python
"""
    Implements sequence viewers for pybioviz
    Created June 2019
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import os,sys,random
import numpy as np
import pandas as pd
from . import utils
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Plot, LinearAxis, Grid, Range1d,CustomJS, Slider, HoverTool, NumeralTickFormatter, Arrow, NormalHead, Label
from bokeh.models.glyphs import Text, Rect
from bokeh.layouts import gridplot, column
import panel as pn
from . import utils

def test_plot(rows=20, cols=100):
    """Bokeh random colors plot"""

    x = np.arange(1, cols)
    y = np.arange(0, rows, 1)    
    xx, yy = np.meshgrid(x, y)
    gx = xx.ravel()
    gy = yy.flatten()
    
    colors = utils.random_colors(len(gx))
    source = ColumnDataSource(dict(x=gx, y=gy, color=colors))    
    plot_height = 50
    x_range = Range1d(0,10, bounds='auto')

    #entire sequence view (no text, with zoom)
    p = figure(title=None, plot_width=800, plot_height=200,
                    tools="pan")
    rects = Rect(x="x", y="y",  width=1, height=1, fill_color="color", line_width=0)
    p.add_glyph(source, rects)
    p.yaxis.visible = False
    p.grid.visible = False  
    #p.title('test bokeh plot')
    p = gridplot([[p]], toolbar_location='below')
    return p

def plot_empty(msg='', plot_width=600, plot_height=200):
    """Return an empty bokeh plot with optional text displayed"""
    
    p = figure(plot_width=plot_width,plot_height=plot_height,tools="",x_range=(0,1),y_range=(0,2))
    text = Label(x=.3, y=1, text=msg)
    p.add_layout(text)
    p.grid.visible = False
    p.toolbar.logo = None
    p.xaxis.visible = False
    p.yaxis.visible = False
    return p

def plot_coverage(df, plot_width=800, plot_height=60, xaxis=True):
    """Plot a bam coverage dataframe returned from get_coverage
    
    Args:
        df: dataframe of coverage data (from get_coverage)
        plot_width: width of plot
        xaxis: plot the x-axis ticks and labels
    """
    
    if df is None or len(df)==0:
        return plot_empty(plot_width=plot_width,plot_height=plot_height)
    df['y'] = df.coverage/2
    source = ColumnDataSource(df)
    x_range = (df.pos.min(),df.pos.max())
    top = df.coverage.max()
    print (top)
    hover = HoverTool(
        tooltips=[            
            ("pos", "@pos"),
            ("coverage", "@coverage")
        ], point_policy='follow_mouse') 
    p = figure(title=None, plot_width=plot_width, plot_height=plot_height,
               x_range=x_range, y_range=(0,top), tools=[hover],
               min_border=0, toolbar_location='right')
    rects = Rect(x="pos", y="y", width=1, height="coverage", fill_color="gray", fill_alpha=0.3)    
    
    p.add_glyph(source, rects)

    p.grid.visible = False
    p.yaxis.visible = False
    if xaxis==False:
        p.xaxis.visible = False
    p.toolbar.logo = None
    return p

def plot_sequence(seq, plot_width=1000, plot_height=20, fontsize='10pt', xaxis=True, tools=""):
    """Plot a single sequence.
    
    Args:
        seq: sequence to plot, a string
        xaxis: display x-axis tick labels or not
        tools: which bokeh tools to display, if needed
    """
    
    if seq is None or len(seq)==0:
        return plotters.plot_empty('no sequence',plot_width=plot_width,plot_height=plot_height)
    text = list(seq)    
    N = len(seq)
    x = np.array(range(N))+1
    
    colors = utils.get_sequence_colors([seq])    
    source = ColumnDataSource(dict(x=x, text=text, colors=colors))  
    x_range = Range1d(0,N, bounds='auto') 
    p = figure(plot_width=plot_width, plot_height=plot_height, x_range=x_range, y_range=(0,1), 
               tools=tools, min_border=0, toolbar_location='below')    
    rects = Rect(x="x", y=0,  width=1, height=2, fill_color="colors", line_color=None, fill_alpha=0.4)
    p.add_glyph(source, rects)
    if len(seq)<200:
        glyph = Text(x="x", y=0, text="text", text_align='center', text_color="black", 
                     text_font="monospace", text_font_size=fontsize)    
        p.add_glyph(source, glyph)
    p.grid.visible = False
    if xaxis == False:
        p.xaxis.visible = False
    else:
        if plot_height<40:
            p.plot_height = 50
        if tools != "":
            p.plot_height = 70
    p.yaxis.visible = False
    p.toolbar.logo = None
    return p

def plot_sequence_alignment(aln, fontsize="8pt", plot_width=800):
    """Bokeh sequence alignment viewer.
    
    Args:
        aln: biopython Multiple Sequence Alignment        
    """
    
    seqs = [rec.seq for rec in (aln)]
    ids = [rec.id for rec in aln]    
    #ids=range(len(seqs))
    text = [i for s in list(seqs) for i in s]
    colors = utils.get_sequence_colors(seqs)    
    cons = utils.get_cons(aln)
    N = len(seqs[0])
    S = len(seqs)    
    width=.4
    
    x = np.arange(1, N+1)
    y = np.arange(0,S,1)
    print (y[:20])
    xx, yy = np.meshgrid(x, y)
    gx = xx.ravel()
    gy = yy.flatten()
    recty = gy+.5
    h= 1/S
    print (N,S)
    #print (text)
    source = ColumnDataSource(dict(x=gx, y=gy, recty=recty, text=text, colors=colors))
    plot_height = len(seqs)*15+50
    x_range = Range1d(0,N+1, bounds='auto')
    if N>100:
        viewlen=100
    else:
        viewlen=N
    view_range = (0,viewlen)
    tools="xpan, xwheel_zoom, reset, save"
    
    #box_select = BoxSelectTool(callback=callback_select)

    #entire sequence view (no text, with zoom)
    p = figure(title=None, plot_width=plot_width, plot_height=50, x_range=x_range, y_range=(0,S), tools=tools, 
                    min_border=0, toolbar_location='below')
    rects = Rect(x="x", y="recty",  width=1, height=1, fill_color="colors", line_color=None, fill_alpha=0.6)
    p.add_glyph(source, rects)
    #p.xaxis.visible = False
    p.yaxis.visible = False
    p.grid.visible = False  
    p.toolbar.logo = None
    
    #sequence text view, zoom fixed
    p1 = figure(title=None, plot_width=plot_width, plot_height=plot_height, x_range=view_range, y_range=ids, tools="xpan,reset", 
                    min_border=0, toolbar_location='below')#, lod_factor=1)          
    glyph = Text(x="x", y="y", text="text", text_align='center',text_color="black", text_font="monospace",text_font_size=fontsize)
    rects = Rect(x="x", y="recty",  width=1, height=1, fill_color="colors", line_color=None, fill_alpha=0.4)
    p1.add_glyph(source, glyph)
    p1.add_glyph(source, rects)
            
    p1.grid.visible = False    
    p1.xaxis.major_label_text_font_style = "bold"
    p1.yaxis.minor_tick_line_width = 0
    p1.yaxis.major_tick_line_width = 0
    
    source2 = ColumnDataSource(dict(x=x, cons=cons))
    
    p3 = figure(title=None, plot_width=plot_width, plot_height=30, x_range=p1.x_range, y_range=(Range1d(min(cons),.5)), tools="xpan")
    rects2 = Rect(x="x", y=0,  width=1, height="cons", fill_color="gray", line_color=None, fill_alpha=0.7)
    p3.add_glyph(source2, rects2)
    
    p3.xaxis.visible = False
    p3.yaxis.visible = False
    p3.grid.visible = False    
    p3.background_fill_color = "beige"

    #p.js_on_change('selected', callback_select)
    jscode="""    
    var start = cb_obj.value;    
    x_range.setv({"start": start, "end": start+l})   
    """
    callback = CustomJS(
        args=dict(x_range=p1.x_range,l=viewlen), code=jscode)
    slider = Slider (start=0, end=N, value=1, step=10)
    slider.js_on_change('value', callback)
    
    p = gridplot([[p],[slider],[p3],[p1]], toolbar_location='below')    
    return p

def plot_features(features, preview=True, x_range=None, fontsize="8pt", plot_width=800, plot_height=150):
    """Bokeh sequence alignment view
    
    """
    
    df = utils.features_to_dataframe(features)#, cds=True)
    df = df[df.type!='region']    
    df['length'] = df.end-df.start
    df['level'] = 1
    df['color'] = utils.random_colors(len(df)) #'green'
    df['x'] = df.start+df.length/2
    df['end_x'] = df.start+50
    df['y'] = [random.choice(range(1,6)) for i in range(len(df))]
    
    #print (df[:3])
    text = df.gene
    S = df.start.min()
    N = df.end.max()+10        
    x = list(df.start+df.length/2)
    h = 20

    source = ColumnDataSource(df)    
        
    viewlen=5000
    if x_range == None:
        x_range = (0,viewlen)
    else:
        #viewlen = int(x_range[1])-int(x_range[0])
        print (x_range,viewlen)    

    hover = HoverTool(
        tooltips=[            
            ("gene", "@gene"),     
            ("locus_tag", "@locus_tag"),
            ("protein_id", "@protein_id"), 
            ("length", "@length"),             
        ],
        #names=['rects']
    )  
    tools=[hover,"xpan, xwheel_zoom, save"]
    
    #sequence text view with ability to scroll along x axis
    p1 = figure(title=None, plot_width=plot_width, plot_height=plot_height, x_range=x_range,
                y_range=(0,10), tools=tools, min_border=0, toolbar_location='right')#, lod_factor=1)
    if viewlen<30000:
        tags = Text(x="x", y="y", y_offset=-10, text="gene", text_align='center',text_color="black", 
                     text_font="monospace",text_font_size=fontsize, name="genetext")
    rects = Rect(x="x", y="y", width="length", height=.4, fill_color="color", fill_alpha=0.4, name='rects')
    arr = Arrow(source=source, x_start="start", x_end="end_x", y_start="y", y_end="y",
                line_color="gray", name='arrows', end=NormalHead(size=8))    
    p1.add_glyph(source, rects)
    p1.add_glyph(source, tags)
    p1.add_layout(arr)
    
    p1.grid.visible = False
    p1.yaxis.visible = False
    p1.xaxis.major_label_text_font_style = "bold"
    p1.yaxis.minor_tick_line_width = 0
    p1.yaxis.major_tick_line_width = 0
    p1.toolbar.logo = None
    p1.xaxis.formatter = NumeralTickFormatter(format="(0,0)")
    
    if preview == True:
        #entire sequence view (no text, with zoom)
        p = figure(title=None, plot_width=plot_width, plot_height=100, x_range=x_range, y_range=(-2,2), tools=tools, 
                        min_border=0, toolbar_location='below')
        rects = Rect(x="x", y="strand", width="length", height=.4, fill_color="colors", line_color='black', fill_alpha=0.6)
        p.add_glyph(source, rects)
        p.yaxis.visible = False
        p.grid.visible = False

        jscode="""    
        var start = cb_obj.value;    
        x_range.setv({"start": start, "end": start+l})   
        """
        callback = CustomJS(
            args=dict(x_range=p1.x_range,l=viewlen), code=jscode)
        slider = Slider (start=1, end=N, value=1, step=100)
        slider.js_on_change('value', callback)
        p = gridplot([[p],[slider],[p1]], toolbar_location='below')
    else:
        p = p1
    return p

def plot_bam_alignment(bam_file, chr, start, end, height=50, fontsize="12pt", plot_width=800, plot_height=250, fill_color='gray'):
    """Bokeh bam alignments plotter.
    Args:
        bam_file: name of a sorted bam file
        start: start of range to show
        end: end of range        
    """
    
    if bam_file is None:
        return plotters.plot_empty('no bam file',plot_width=plot_width, plot_height=plot_height)
    
    h=.6+height/plot_height
    #get outer ranges to retrieve reads from so that we
    #cover the visible range from start-end
    o = (end-start)/2
    #get reads in range into a dataframe
    df = utils.get_bam_aln(bam_file, chr, start-o, end+o)
    if df is None:
        p = plotters.plot_empty('no bam file or bam not indexed')
        return p
    #offset for rects
    df['x'] = df.start+df.length/2
    #set colors by quality
    df['color'] = df.apply(lambda x: 'red' if x.mapq==0 else fill_color ,1)
    df['span'] = df.apply(lambda x: str(x.start)+':'+str(x.end),1)
    print (len(df))
    
    source = ColumnDataSource(df)
    x_range=(start, end)
    hover = HoverTool(
        tooltips=[            
            ("name", "@name"),
            ("cigar", "@cigar"),
            ("span", "@span"),
            ("length", "@length"),
            ("mapq", "@mapq"),
            ("counts", "@counts")
        ],
        point_policy='follow_mouse',
    )
    tools=[hover,"ypan","save"]
    
    p = figure(title=None, plot_width=plot_width, plot_height=plot_height, x_range=x_range, y_range=(0,height), tools=tools, 
                    min_border=0, toolbar_location='right')
    rects = Rect(x="x", y="y", width="length", height=h, fill_color="color", line_color='gray',fill_alpha=0.4)
    #if start-end > 100:
    p.ygrid.visible = False
    p.add_glyph(source, rects)
    p.yaxis.visible = False
    p.xaxis.formatter = NumeralTickFormatter(format="(0,0)")
    p.toolbar.logo = None
    return p