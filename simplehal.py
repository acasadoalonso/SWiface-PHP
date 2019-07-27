"""
Classes encapsulating the structure of a HAL Document.
"""

try:
    import json
except ImportError:
    import simplejson as json

from uritemplate import expand

from copy import deepcopy

VALID_LINK_ATTRS = ['templated', 'type', 'name', 'profile', 'title',
                    'hreflang']


class HalDocument(object):
    """
    A single HAL document, which can be nested in
    another.
    """

    def __init__(self, links, data=None, embed=None):
        if data:
            self.structure = data
        else:
            self.structure = {}
        if embed:
            self.structure['_embedded'] = embed
        self.structure['_links'] = links.structure

    def to_json(self):
        """
        Dump the structure of the document as JSON.
        """
        return json.dumps(self.structure)

    def get_curies(self):
        """
        Get a mapping of curies to URIs.
        """
        curies = {}
        try:
            curie_links = self.structure['_links']['curie']
            if not hasattr(curie_links, 'append'):
                curie_links = [curie_links]
            for link in curie_links:
                curies[link['name']] = link['href']
        except KeyError:
            pass
        return curies

    def get_data(self, data_type=None):
        """
        Return data. First look in embeded, then the rest of the
        structure. Should we append instead of exclusive here?
        """
        if data_type:
            try:
                return self.structure['_embedded'][data_type]
            except KeyError:
                return self.structure[data_type]
        else:
            data = {}
            for item in list(self.structure.keys()):
                if item not in ['_links', '_embedded']:
                    data[item] = self.structure[item]
            try:
                data['_embedded'] = self.structure['_embedded']
            except KeyError:
                pass
            return data

    @property
    def links(self):
        """
        Accessor for the links. Read only.
        """
        return self.structure['_links']

    @classmethod
    def from_json(cls, input_string):
        """
        Create a new document from provided input string.
        That string should be JSON.
        """
        info = json.loads(input_string)
        return cls.from_python(info)

    @classmethod
    def from_python(cls, structure):
        """
        Create a new document from provided structure.
        Usually decoded from JSON.
        """
        structure = deepcopy(structure)

        links = Links()
        for link in structure['_links']:
            rel = link
            target = structure['_links'][rel]
            if hasattr(target, 'append'):
                for item in target:
                    href = item['href']
                    del item['href']
                    links.add(Link(rel, href, **item))
            else:
                href = target['href']
                del target['href']
                links.add(Link(rel, href, **target))

        if '_links' in structure:
            del structure['_links']

        try:
            embedded = structure['_embedded']
            del structure['_embedded']
        except KeyError:
            embedded = None

        return cls(links, data=structure, embed=embedded)


class Links(object):
    """
    Model of a HAL links collection.
    """

    def __init__(self):
        self.structure = {}

    def add(self, *links):
        """
        Add some link. For a new link, add it singular. If
        there is a second of the same rel, become plural
        (that is, a list).
        """
        for link in links:
            if link.rel in self.structure:
                self.structure[link.rel] = [self.structure[link.rel]]
                self.structure[link.rel].append(link.to_dict())
            else:
                self.structure[link.rel] = link.to_dict()


class Link(object):
    """
    Model of a HAL link.
    """

    def __init__(self, rel, href, **kwargs):
        self.rel = rel
        self.href = href
        self.kwargs = kwargs

    def to_dict(self):
        """
        Turn the link into a dictionary.
        """
        result = {'href': self.href}
        for key in self.kwargs:
            if key in VALID_LINK_ATTRS:
                result[key] = self.kwargs[key]
        return result


class Resolver(object):
    """
    Resolve curry links.
    """

    def __init__(self, curie_map):
        self.map = curie_map

    def expand(self, link):
        if ':' in link:
            (name, rel) = link.split(':', 1)
            try:
                return expand(self.map[name], {'rel': rel})
            except KeyError:
                pass
        return link
