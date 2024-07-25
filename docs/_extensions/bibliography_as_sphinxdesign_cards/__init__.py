#!/usr/bin/env python3

"""Modify the bibliography entries created by sphinxcontrib.bibtex to be sphinx-design cards."""

# The default `:::{bibliography}` blocks are not very nicely formatted.
# In the docutils tree, they look like this:
#
# <citation backrefs="id2" docname="user-guide/user-manual/travel-time-matrices" ids="fink-r5py-2022">
#     <label support_smartquotes="False">
#         Fink et al., 2022
#     </label>
#     <paragraph>
#         Fink, C., Klumpenhouwer, W., Saraiva, M., Pereira, R., & Tenkanen, H.
#         (2022 , September). <emphasis>r5py: Rapid Realistic Routing with R5 in
#         Python</emphasis>.
#         <reference refuri="https://doi.org/10.5281/ZENODO.7060437">
#             DOI:10.5281/ZENODO.7060437
#         </reference>
#     </paragraph>
# </citation>
#
# After experimenting with `sphinx-design`’s cards in the data-requirements.md
# and also in early versions of the citations.md documents, I started to like
# their look also for the references: They are prominent, cleanly formatted, and
# can be clicked as a whole.
#
# In the docutil tree, they would look like this:
#
# <container classes="sd-card sd-sphinx-override sd-mb-3 sd-shadow-sm sd-card-hover" design_component="card" is_div="True">
#     <container classes="sd-card-body" design_component="card-body" is_div="True">
#         <paragraph classes="sd-card-text">
#             Fink, C., Klumpenhouwer, W., Saraiva, M., Pereira, R., & Tenkanen,
#             H., 2022: <emphasis>r5py: Rapid Realistic Routing with R⁵ in Python</emphasis>.
#             <reference refuri="https://doi.org/10.5281/zenodo.7060437">
#                   DOI:10.5281/zenodo.7060437
#             </reference>
#         </paragraph>
#     </container>
#     <PassthroughTextElement>
#         <reference classes="['sd-stretched-link']" refuri="https://doi.org/10.5281/zenodo.7060437"/>
#     </PassthroughTextElement>
# </container>
#
# This sphinx extension triggers at a very late stage of running sphinx,
# searches for all <citations>, and converts them from the above subtree
# to the below format
# It uses the sphinx.transforms.post_transform hook, see
# https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events


import docutils.nodes
import sphinx.transforms.post_transforms
import sphinx_design.shared


__version__ = "0.0.1"


class CitationsToSphinxDesignCardsTransformer(
    sphinx.transforms.post_transforms.SphinxPostTransform
):
    """Modify the bibliography entries created by sphinxcontrib.bibtex to be sphinx-design cards."""

    default_priority = (
        198  # before anything from sphinx_design, but after sphinxcontrib.bibtex
    )

    def apply(self, **kwargs):
        """Apply the transformation to all relevant nodes."""
        for node in self.document.findall(docutils.nodes.citation):
            self.handle(node)

    def handle(self, node):
        """Modify a single node."""
        new_node = self._create_empty_sdcard_container()
        for attribute in ["backrefs", "docname", "ids"]:
            new_node[attribute] = node[attribute]

        # paragraph (first child of first child), see _create_empty...()
        new_paragraph = new_node[0][0]
        old_paragraph = node[node.first_child_matching_class(docutils.nodes.paragraph)]
        new_paragraph.children = old_paragraph.children

        # convert <tt> (docutils.nodes.literal) into more nicely formatted titles
        # (see also format_title() in ../_helpers/citation_style.py)
        for tt in new_paragraph.findall(docutils.nodes.literal):
            span = docutils.nodes.inline(classes=["article-title"])
            span += tt.children
            new_paragraph.replace(tt, span)

        if r := new_paragraph.first_child_matching_class(docutils.nodes.reference):
            old_reference = new_paragraph[r]
            new_reference = sphinx_design.shared.PassthroughTextElement()
            new_reference += docutils.nodes.reference(
                classes=["sd-stretched-link"],
                refuri=old_reference["refuri"],
            )
            new_node += new_reference

        # node.replace_self(new_node)  # <- does not work - why?
        node.parent.replace(node, new_node)

    @staticmethod
    def _create_empty_sdcard_container():
        container = docutils.nodes.container(
            classes=[
                "sd-card",
                "sd-sphinx-override",
                "sd-mb-3",
                "sd-shadow-sm",
                "sd-card-hover",
            ],
            design_component="card",
            is_div="True",
        )
        container += docutils.nodes.container(
            classes=["sd-card-body"],
            design_component="card-body",
            is_div="True",
        )
        container[0] += docutils.nodes.paragraph(
            classes=["sd-card-text"],
        )
        return container


def setup(app):
    """
    Register extension with sphinx.

    This is a callback function called by sphinx when it loads the extension.
    """
    app.add_post_transform(CitationsToSphinxDesignCardsTransformer)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": False,  # not sure, but let’s err on the safe side
    }
