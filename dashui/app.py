# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100


from arcs import app

def main():
    import sys
    if len(sys.argv)>1 and sys.argv[1] == 'debug':
        app.run_server(debug=True)
    else:
        from waitress import serve
        serve(app.server, host='0.0.0.0', port=8050)
    
if __name__ == '__main__': main()

