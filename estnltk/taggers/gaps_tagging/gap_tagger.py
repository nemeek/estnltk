from collections import defaultdict

from estnltk.spans import Span
from estnltk.layer import Layer
from estnltk.taggers import TaggerNew


class GapTagger(TaggerNew):
    """ Tags all text regions that are not covered by any span of any input layer.
        These regions can be trimmed by trim function and annotated by decorator function.
    """
    description = 'Tags gaps of input layers.'
    attributes = ()
    conf_param = ['decorator', 'trim']

    def __init__(self, layer_name, input_layers, trim=None, attributes=(), decorator=None):
        self.depends_on = input_layers
        self.layer_name = layer_name
        self.trim = trim
        assert bool(attributes) == bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.attributes = tuple(attributes)
        self.decorator = decorator

    def _change_layer(self, text, input_layers, status):
        raise NotImplementedError

    def _make_layer(self, raw_text, input_layers, status):
        layer = Layer(
            name=self.layer_name,
            attributes=self.attributes,
            parent=None,
            enveloping=None,
            ambiguous=False
            )
        layers = list(input_layers.values())
        for start, end in find_gaps(layers, len(raw_text)):
            assert start < end
            if self.trim:
                t = self.trim(raw_text[start:end])
                start = raw_text.find(t, start)
                end = start + len(t)
            if start < end:
                span = Span(start, end)
                if self.decorator:
                    decorations = self.decorator(raw_text[start:end])
                    for attr in self.attributes:
                        setattr(span, attr, decorations[attr])
                layer.add_span(span)
        return layer


def find_gaps(layers, text_length):
    cover_change = defaultdict(int)
    for layer in layers:
        for span in layer.spans:
            cover_change[span.start] += 1
            cover_change[span.end] -= 1
    indexes = sorted(cover_change)
    if indexes[0] > 0:
        yield (0, indexes[0])
    cover = 0
    for i, j in zip(indexes, indexes[1:]):
        cover += cover_change[i]
        assert cover >= 0
        if not cover:
            yield (i, j)
    assert not cover + cover_change[indexes[-1]]
    if indexes[-1] < text_length:
        yield (indexes[-1], text_length)