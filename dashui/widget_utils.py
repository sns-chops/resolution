import flask, io, numpy as np

def send_file(nparr, attachment_filename):
    str_io = io.StringIO()
    np.savetxt(str_io, nparr, delimiter=',')
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(
        mem,
        mimetype='text/csv',
        download_name=attachment_filename,
        as_attachment=True)


def polyfit(x, y, order=3):
    "fit data to polynomial, and return python and matlab formula texts"
    a = np.polyfit(x, y, order)
    yfit = sum( a[i]*x**(order-i) for i in range(order+1) )
    # formula = r''.join( r'%.5g \times E ^ %d' % (a[i], order-i) for i in range(order+1) )
    # formula = r'$$'+formula+r'$$'
    def _(exponent, power_operator):
        if exponent>1: return '* x%s%d'%(power_operator, exponent)
        if exponent==1: return '* x'
        return ''
    python_formula = 'Python: ' + ' '.join( '%+.5g %s' % (a[i], _(order-i, '**')) for i in range(order+1) )
    matlab_formula = 'Matlab: ' + ' '.join( '%+.5g %s' % (a[i], _(order-i, '^')) for i in range(order+1) )
    return yfit, python_formula, matlab_formula
