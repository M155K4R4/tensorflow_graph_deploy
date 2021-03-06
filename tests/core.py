# -*- coding: utf-8 -*-


import numpy as np
from .base import TestCase, tfdeploy as td


__all__ = ["CoreTestCase"]


class CoreTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(CoreTestCase, self).__init__(*args, **kwargs)

        self.simple_model = td.Model()
        y, sess = self.get("simple", "y", "sess")
        self.simple_model.add(y, tf_sess=sess)

    def test_tensors(self):
        m = self.simple_model

        # model has one root tensor ...
        self.assertEqual(len(m.roots), 1)

        # ... which is named "output" and can be retrieved via get
        outp = m.get("output")
        self.assertIn(outp, m.roots.values())

        # the input tensor is named "input"
        self.assertIsNotNone(m.get("input"))

    def test_ops(self):
        m = self.simple_model
        op = m.get("output").op

        # the root tensor operator is a softmax op ...
        self.assertIsInstance(op, td.Softmax)

        # ... and has one input ...
        self.assertEqual(len(op.inputs), 1)

        # ... whose op is an add op
        self.assertIsInstance(op.inputs[0].op, td.Add)

    def test_eval(self):
        m = self.simple_model
        inp, outp, kp = m.get("input", "output", "keep_prob")

        # create an input batch
        examples = np.random.rand(1000, 10).astype("float32")

        # first, eval using tf
        x, y, keep_prob, sess = self.get("simple", "x", "y", "keep_prob", "sess")
        rtf = y.eval(session=sess, feed_dict={x: examples, keep_prob: 1.0})

        # then, eval using td
        rtd = outp.eval({inp: examples, kp: 1.0})

        # no element in the diff array should be larger than 1e-7
        maxdiff = np.max(np.abs(rtf - rtd))
        self.assertLess(maxdiff, 1e-7)
