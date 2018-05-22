const test = require('tape');
const PyFi = require('../');

test('pyfi_message', (t) => {
  t.plan(2);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      from: 'message_test',
      import: 'message_me',
    }],
  });
  py._.onReady(() => {
    py.message_me()
      .onMessage((message) => {
        t.equal(message, 'messaging');
      })
      .then((res) => {
        t.equal(res, 'done_messaging');
        py._.end();
      })
      .catch((error) => {
        t.fail(error);
        py._.end();
      });
  });
});
