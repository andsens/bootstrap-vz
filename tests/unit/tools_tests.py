import os
from nose.tools import eq_
from bootstrapvz.common.tools import log_call

subprocess_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'subprocess.sh')


def setup_logger():
    import logging
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)

    import StringIO
    output = StringIO.StringIO()
    string_handler = logging.StreamHandler(output)
    string_handler.setLevel(logging.DEBUG)
    root.addHandler(string_handler)
    return output


def test_log_call_output_order():
    logged = setup_logger()
    fixture = """
2 0.0 one\\\\n
1 0.4 two\\\\n
1 0.4 four\\\\n
2 0.4 No, three..\\\\n
1 0.4 three\\\\n
"""
    status, stdout, stderr = log_call([subprocess_path], stdin=fixture)
    eq_(status, 0)
    eq_(stderr, ['one', 'No, three..'])
    eq_(stdout, ['two', 'four', 'three'])
    expected_order = ['one',
                      'two',
                      'four',
                      'No, three..',
                      'three',
                      ]
    eq_(expected_order, logged.getvalue().split("\n")[8:-1])
