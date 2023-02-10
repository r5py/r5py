#!/usr/bin/env python3


"""Modify sphinxcontrib.bibtex so that the reference style is closer to what’s used in transport geography."""


import dataclasses
import typing

import pybtex.plugin
import pybtex.richtext
import sphinxcontrib.bibtex.style.referencing
import sphinxcontrib.bibtex.style.referencing.author_year
import sphinxcontrib.bibtex.style.referencing.basic_author_year
import sphinxcontrib.bibtex.style.referencing.extra_author
import sphinxcontrib.bibtex.style.referencing.extra_empty
import sphinxcontrib.bibtex.style.referencing.extra_label
import sphinxcontrib.bibtex.style.referencing.extra_year
import sphinxcontrib.bibtex.style.template


__all__ = ["R5PY_CITATION_STYLE", "R5PY_REFERENCE_STYLE"]


# Use APA style, provided upstream by https://github.com/cproctor/pybtex-apa7-style
R5PY_CITATION_STYLE = pybtex.plugin.find_plugin("pybtex.style.formatting", "apa7").name

# Define a (custom) name for the style we create below
R5PY_REFERENCE_STYLE = "author_year_apa7_full_link"


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
