import flask, io, numpy as np

def send_file(nparr, filename):
    str_io = io.StringIO()
    np.savetxt(str_io, nparr, delimiter=',')
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(
        mem,
        mimetype='text/csv',
        attachment_filename=filename,
        as_attachment=True)

