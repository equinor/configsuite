"""Copyright 2018 Equinor ASA and The Netherlands Organisation for
Applied Scientific Research TNO.

Licensed under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the conditions stated in the LICENSE file in the project root for
details.

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
"""

from docutils import nodes

import yaml


class cs_container(nodes.General, nodes.Element):
    pass


class cs_header(nodes.General, nodes.Element):
    pass


class cs_content(nodes.General, nodes.Element):
    pass


class cs_children(nodes.General, nodes.Element):
    pass


def visit_container(self, node):
    self.body.append(self.starttag(node, "div"))


def depart_container(self, node):

    if node.hasattr("example") and node["example"] is not None:
        example_doc = yaml.dump(node["example"], indent=4)
        example_doc = example_doc.replace("\n", "<br>")
        example_doc = example_doc.replace("    ", "&nbsp;&nbsp;")
        self.body.append(
            (
                "<div class='cs_content'>Example:<br>"
                "<code class='cs_code'>{}</code><br></div>"
            ).format(example_doc)
        )
    self.body.append("</div><br>")


def visit_header(self, node):
    self.body.append(self.starttag(node, "div"))
    self.body.append("<h3>{}</h3><br>".format(node.get("text")))


def depart_header(self, _):
    self.body.append("</div><br>")


def visit_content(self, node):
    self.body.append(self.starttag(node, "div"))


def depart_content(self, _):
    self.body.append("</div><br>")


def visit_children(self, node):
    self.body.append(self.starttag(node, "div"))


def depart_children(self, _):
    self.body.append("</div><br>")
