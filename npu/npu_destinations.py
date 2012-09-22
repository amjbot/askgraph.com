

import json


def ideal_render( wmem, format ):
    if format=='json':
        return json.dumps(wmem)
    elif format=='html':
        return 'html'
    else:
        raise Exception('Unknown npu destination: %s' % format)
