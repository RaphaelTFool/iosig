import os, sys, datetime, string

iosig_home = os.getenv('IOSIG_HOME')
lib_path = os.path.join(iosig_home, 'src', 'analysis')
sys.path.append(lib_path)
import prop
from prop import *

from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import Blueprint

app = Flask(__name__)
iosig_data_path = os.getenv('IOSIG_DATA')
print 'root path: ', app.root_path
iosig_data = Blueprint('iosig_data', __name__, url_prefix='/iosig_data', static_folder=iosig_data_path)
app.register_blueprint(iosig_data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@app.route('/iosig')
def list_trace_dirs():
    # list the $IOSIG_DATA
    #iosig_data_path = os.getenv('IOSIG_DATA')
    if (iosig_data_path == None):
        return render_template('trace_dirs.html', list=None)
    dirs = [ trace_dir for trace_dir in os.listdir(iosig_data_path) if os.path.isdir(os.path.join(iosig_data_path, trace_dir)) ]
    dirs.sort(reverse=True)
    dirs_list = []
    for directory in dirs:
        user, separator, the_rest = directory.partition('_')
        ts_epoch, separator, exe_name = the_rest.partition('_')
        date_string = datetime.datetime.fromtimestamp(float(ts_epoch)).strftime('%Y-%m-%d %H:%M:%S')
        global_stat = Properties()
        f_stat = open(os.path.join(iosig_data_path, directory, 'result_output', 'global.stat.properties'))
        global_stat.load(f_stat)
        
        dirs_list.append(
                (user, date_string, exe_name, directory, 
                    round(float(global_stat['global_exe_time']), 6), 
                    global_stat['global_read_count'], 
                    round(float(global_stat['global_read_time_nonoverlap']), 6), 
                    global_stat['global_write_count'], 
                    round(float(global_stat['global_write_time_nonoverlap']), 6) )
                )

    return render_template('iosig_list.html', list=dirs_list)

@app.route('/details/<trace_id>')
def show_trace_details(trace_id):
    #iosig_data_path = os.getenv('IOSIG_DATA')
    trace_data_path = os.path.join(iosig_data_path, trace_id)
    analysis_result_path = os.path.join(trace_data_path, 'result_output')
    sub_path = os.path.join(trace_id, 'result_output')
    if os.path.exists(analysis_result_path) == False:
        return render_template('iosig_details.html', trace_id=None)

    #figures = [ os.path.join(sub_path, figure) for figure in os.listdir(analysis_result_path) if figure.endswith('png') ]
    #figures.sort()
    iorate_figures = [ os.path.join(sub_path, figure) for figure in os.listdir(analysis_result_path) if figure.endswith('iorate.png') ]
    #access_hole_figures = [ os.path.join(sub_path, figure) for figure in os.listdir(analysis_result_path) if figure.endswith('hole.png') ]
    iorate_figures.sort()
    #access_hole_figures.sort()
    # TODO: access hole figures may not be generated
    figure_list = []
    iorate_figures_count = len(iorate_figures)

    for i in range(iorate_figures_count):
        proc_info = (iorate_figures[i].partition("."))[0]
        r_index = string.rfind(proc_info, '_')
        proc_info = string.upper(proc_info[r_index+1:])
        iorate_figure = None
        hole_figure = None
        if os.path.getsize(os.path.join(iosig_data_path, iorate_figures[i])) > 0:
            iorate_figure = iorate_figures[i]
        #if os.path.getsize(os.path.join(iosig_data_path, access_hole_figures[i])) > 0:
        #    hole_figure = access_hole_figures[i]
        figure_list.append((proc_info, iorate_figure, hole_figure))
    return render_template('iosig_details.html', trace_id=trace_id, figure_list=figure_list)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

