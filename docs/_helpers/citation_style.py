#!/usr/bin/env python3


"""Modify sphinxcontrib.bibtex so that the reference style is closer to what’s used in transport geography."""


# The modifications below change two different parts of how citations are
# formatted by sphinxcontrib.bibtex.
#
# On the one hand, the format of citations (in the text) is governed by
# sphinxcontrib.bibtex’s own `sphinxcontrib.bibtex.style.referencing`,
# see its documentation, here:
# https://sphinxcontrib-bibtex.readthedocs.io/en/2.5.0/usage.html#custom-inline-citation-references
#
# On the other hand, the format of bibliographies (lists of references, inserted,
# for instance, on the bottom of a page, using `:::{bibliography}` markup) is
# defined in pybtex.style.formatting classes (see also sphinxcontrib-bibtex’
# documentation:
# https://sphinxcontrib-bibtex.readthedocs.io/en/2.5.0/usage.html#custom-formatting-sorting-and-labelling
#
# There is an almost-perfect APA style implemented in `pybtex-apa7-style`;
# however, (1) it does not add DOIs to entries referring to bibtex’ @misc categories,
# which includes Zenodo software packages. It would be nice, if people could
# actually see the reference we ask them to cite. Also, (2) it uses the default
# sphinxcontrib-bibtex formatting of the inline citations, which means it uses
# (a) brackets around the publication year, and (b) makes _only_ the year clickable.
#
# That’s why, below, I first define two custom names for our citation and reference
# styles (these are then imported by `conf.py`), and then create (I) a pybtex.BaseStyle
# to define the format of the bibliography entries, and (II) a custom
# sphinxcontrib.bibtex.ReferenceStyle that substitutes brackets with parentheses and
# formats the entire citation as a link.


import dataclasses
import typing

import pybtex.plugin
import pybtex.richtext
import pybtex.style.formatting
import pybtex.style.template
import sphinxcontrib.bibtex.style.referencing
import sphinxcontrib.bibtex.style.referencing.author_year
import sphinxcontrib.bibtex.style.referencing.basic_author_year
import sphinxcontrib.bibtex.style.referencing.extra_author
import sphinxcontrib.bibtex.style.referencing.extra_empty
import sphinxcontrib.bibtex.style.referencing.extra_label
import sphinxcontrib.bibtex.style.referencing.extra_year
import sphinxcontrib.bibtex.style.template


__all__ = ["R5PY_CITATION_STYLE", "R5PY_REFERENCE_STYLE"]


# Define (custom) names for the styles we create below
R5PY_CITATION_STYLE = "apa7_with_doi_for_misc"
R5PY_REFERENCE_STYLE = "author_year_apa7_full_link"


# -----------------------------------------------------------
# (I) custom pybtex style for the bibliography/reference list
# -----------------------------------------------------------


# Use APA style, provided upstream by https://github.com/cproctor/pybtex-apa7-style,
# and modify it to output DOIs for @misc entries (e.g., our Zenodo link)
class ApaMiscDoiStyle(pybtex.plugin.find_plugin("pybtex.style.formatting", "apa7")):
    name = R5PY_CITATION_STYLE

    def format_date(self, e):
        return pybtex.style.template.join[
            "(",
            pybtex.style.template.first_of[
                pybtex.style.template.optional[pybtex.style.template.field("year")],
                "n.d.",
            ],
            "):",
        ]

    def format_doi(self, e):
        return pybtex.style.template.href[
            pybtex.style.template.join[
                "https://doi.org/", pybtex.style.template.field("doi", raw=True)
            ],
            pybtex.style.template.join[
                "DOI:", pybtex.style.template.field("doi", raw=True)
            ],
        ]

    def format_title(self, e, which_field, as_sentence=True):
        formatted_title = pybtex.style.template.tag("tt")[
            pybtex.style.template.field(
                which_field, apply_func=lambda text: text.capitalize()
            )
        ]
        if as_sentence:
            return pybtex.style.template.sentence[formatted_title]
        else:
            return formatted_title

    def get_misc_template(self, e):
        if "author" in e.persons:
            return pybtex.style.formatting.toplevel[
                self.format_names("author"),
                self.format_date(e),
                pybtex.style.template.optional[self.format_title(e, "title")],
                pybtex.style.template.sentence[
                    pybtex.style.template.optional_field("note")
                ],
                self.format_web_refs(e),
            ]
        else:
            return pybtex.style.formatting.toplevel[
                pybtex.style.template.optional[self.format_btitle(e, "title")],
                self.format_date(e),
                pybtex.style.template.sentence[
                    pybtex.style.template.optional_field("note")
                ],
                self.format_web_refs(e),
            ]


# Register this custom Style as a pybtex plugin
pybtex.plugin.register_plugin(
    "pybtex.style.formatting", R5PY_CITATION_STYLE, ApaMiscDoiStyle
)


# -----------------------------------------------------------
# (II) custom sphinxcontrib-bibtex style for inline citations
# -----------------------------------------------------------


# Change square brackets to round parentheses
@dataclasses.dataclass
class ParenthesisStyle(sphinxcontrib.bibtex.style.referencing.BracketStyle):
    left: typing.Union["pybtex.richtext.BaseText", str] = "("
    right: typing.Union["pybtex.richtext.BaseText", str] = ")"


# Make entire reference text the link to the bibliography entry
# (by default, only the year is clickable/blue)
@dataclasses.dataclass
class BasicAuthorYearTextualFullLinkReferenceStyle(
    sphinxcontrib.bibtex.style.referencing.basic_author_year.BasicAuthorYearTextualReferenceStyle
):
    def inner(self, role_name: str) -> "pybtex.style.template.Node":
        return sphinxcontrib.bibtex.style.template.reference[
            sphinxcontrib.bibtex.style.template.join(sep=self.text_reference_sep)[
                self.person.author_or_editor_or_title(full="s" in role_name),
                sphinxcontrib.bibtex.style.template.join[
                    self.bracket.left,
                    sphinxcontrib.bibtex.style.template.year,
                    self.bracket.right,
                ],
            ]
        ]


# Put the above changes together:
# - parentheses instead of brackets
# - fully clickable reference
@dataclasses.dataclass
class AuthorYearParenthesisFullLinkReferenceStyle(
    sphinxcontrib.bibtex.style.referencing.author_year.AuthorYearReferenceStyle
):
    bracket_textual: sphinxcontrib.bibtex.style.referencing.BracketStyle = (
        dataclasses.field(default_factory=ParenthesisStyle)
    )
    bracket_parenthetical: sphinxcontrib.bibtex.style.referencing.BracketStyle = (
        dataclasses.field(default_factory=ParenthesisStyle)
    )
    bracket_author: sphinxcontrib.bibtex.style.referencing.BracketStyle = (
        dataclasses.field(default_factory=ParenthesisStyle)
    )
    bracket_label: sphinxcontrib.bibtex.style.referencing.BracketStyle = (
        dataclasses.field(default_factory=ParenthesisStyle)
    )
    bracket_year: sphinxcontrib.bibtex.style.referencing.BracketStyle = (
        dataclasses.field(default_factory=ParenthesisStyle)
    )

    def __post_init__(self):
        self.styles.extend(
            [
                sphinxcontrib.bibtex.style.referencing.basic_author_year.BasicAuthorYearParentheticalReferenceStyle(
                    bracket=self.bracket_parenthetical,
                    person=self.person,
                    author_year_sep=self.author_year_sep,
                ),
                BasicAuthorYearTextualFullLinkReferenceStyle(  # <- our custom Style class
                    bracket=self.bracket_textual,
                    person=self.person,
                    text_reference_sep=self.text_reference_sep,
                ),
                sphinxcontrib.bibtex.style.referencing.extra_author.ExtraAuthorReferenceStyle(
                    bracket=self.bracket_author, person=self.person
                ),
                sphinxcontrib.bibtex.style.referencing.extra_label.ExtraLabelReferenceStyle(
                    bracket=self.bracket_label
                ),
                sphinxcontrib.bibtex.style.referencing.extra_year.ExtraYearReferenceStyle(
                    bracket=self.bracket_year
                ),
                sphinxcontrib.bibtex.style.referencing.extra_empty.ExtraEmptyReferenceStyle(),
            ]
        )

        # initialise only the grandparent, not super() (self.styles would be extended twice)
        sphinxcontrib.bibtex.style.referencing.GroupReferenceStyle.__post_init__(self)


# Register this custom style with sphinxcontrib.bibtex,
# using the name defined above
sphinxcontrib.bibtex.plugin.register_plugin(
    "sphinxcontrib.bibtex.style.referencing",
    R5PY_REFERENCE_STYLE,
    AuthorYearParenthesisFullLinkReferenceStyle,
)
