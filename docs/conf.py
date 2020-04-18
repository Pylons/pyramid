# -*- coding: utf-8 -*-
#
# pyramid documentation build configuration file, created by
# sphinx-quickstart on Wed Jul 16 13:18:14 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import sys
import os
import datetime
import inspect
import warnings

warnings.simplefilter('ignore', DeprecationWarning)

import pkg_resources
import pylons_sphinx_themes

# skip raw nodes
from sphinx.writers.text import TextTranslator
from sphinx.writers.latex import LaTeXTranslator

from docutils import nodes
from docutils import utils
from docutils.parsers.rst import Directive


def raw(*arg):
    raise nodes.SkipNode
TextTranslator.visit_raw = raw


# make sure :app:`Pyramid` doesn't mess up LaTeX rendering
def nothing(*arg):
    pass
LaTeXTranslator.visit_inline = nothing
LaTeXTranslator.depart_inline = nothing

book = os.environ.get('BOOK')

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'repoze.sphinx.autointerface',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinxcontrib.autoprogram',
    # enable pylons_sphinx_latesturl when this branch is no longer "latest"
    # 'pylons_sphinx_latesturl',
    ]

# Looks for objects in external projects
intersphinx_mapping = {
    'colander': ('https://docs.pylonsproject.org/projects/colander/en/latest/', None),
    'cookbook': ('https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/', None),
    'deform': ('https://docs.pylonsproject.org/projects/deform/en/latest/', None),
    'jinja2': ('https://docs.pylonsproject.org/projects/pyramid-jinja2/en/latest/', None),
    'pylonswebframework': ('https://docs.pylonsproject.org/projects/pylons-webframework/en/latest/', None),
    'python': ('https://docs.python.org/3/', None),
    'pytest': ('https://docs.pytest.org/en/latest/', None),
    'sqla': ('https://docs.sqlalchemy.org/en/latest/', None),
    'tm': ('https://docs.pylonsproject.org/projects/pyramid-tm/en/latest/', None),
    'toolbar': ('https://docs.pylonsproject.org/projects/pyramid-debugtoolbar/en/latest/', None),
    'transaction': ('https://transaction.readthedocs.io/en/latest/', None),
    'tutorials': ('https://docs.pylonsproject.org/projects/pyramid-tutorials/en/latest/', None),
    'venusian': ('https://docs.pylonsproject.org/projects/venusian/en/latest/', None),
    'webtest': ('https://docs.pylonsproject.org/projects/webtest/en/latest/', None),
    'zcml': (
    'https://docs.pylonsproject.org/projects/pyramid-zcml/en/latest/', None),
}


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'The Pyramid Web Framework'
thisyear = datetime.datetime.now().year
copyright = '2008-%s, Agendaless Consulting' % thisyear

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = pkg_resources.get_distribution('pyramid').version

# The full version, including alpha/beta/rc tags.
release = version

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_themes/README.rst', ]

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = book and 'bw' or 'tango'
if book:
    pygments_style = 'bw'

# Options for HTML output
# -----------------------
# enable pylons_sphinx_latesturl when this branch is no longer "latest"
# pylons_sphinx_latesturl_base = (
#     'https://docs.pylonsproject.org/projects/pyramid/en/latest/')
# pylons_sphinx_latesturl_pagename_overrides = {
#     # map old pagename -> new pagename
#     'whatsnew-1.0': 'index',
#     'whatsnew-1.1': 'index',
#     'whatsnew-1.2': 'index',
#     'whatsnew-1.3': 'index',
#     'whatsnew-1.4': 'index',
#     'whatsnew-1.5': 'index',
#     'whatsnew-1.6': 'index',
#     'whatsnew-1.7': 'index',
#     'whatsnew-1.8': 'index',
#     'whatsnew-1.9': 'index',
#     'whatsnew-1.10': 'index',
#     'tutorials/gae/index': 'index',
#     'api/chameleon_text': 'api',
#     'api/chameleon_zpt': 'api',
# }

html_theme = 'pyramid'
html_theme_path = pylons_sphinx_themes.get_html_themes_path()
html_theme_options = dict(
    github_url='https://github.com/Pylons/pyramid',
    # On master branch and new branch still in
    # pre-release status: true; else: false.
    in_progress='true',
    # On branches previous to "latest": true; else: false.
    outdated='false',
    )

# Control display of sidebars
html_sidebars = {'**': [
    'localtoc.html',
    'ethicalads.html',
    'relations.html',
    'sourcelink.html',
    'searchbox.html',
]}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = 'The Pyramid Web Framework v%s' % release

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Do not use smart quotes.
smartquotes = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'pyramid'

# Options for LaTeX output
# ------------------------

latex_engine = 'xelatex'
latex_use_xindy = False

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '10pt'

latex_additional_files = [
    '_static/latex-note.png',
    '_static/latex-warning.png',
]

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('latexindex', 'pyramid.tex',
   'The Pyramid Web Framework',
   'Chris McDonough', 'manual'),
    ]

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_toplevel_sectioning = "section"

# If false, no module index is generated.
latex_domain_indices = False

## Say, for a moment that you have a twoside document that needs a 3cm
## inner margin to allow for binding and at least two centimetres the
## rest of the way around. You've been using the a4wide package up until
## now, because you like the amount of text it places on the
## page. Perhaps try something like this in your preamble:

## \usepackage[bindingoffset=1cm,textheight=22cm,hdivide={2cm,*,2cm},vdivide={*,22cm,*}]{geometry}

## _PREAMBLE = r"""\usepackage[bindingoffset=0.45in,textheight=7.25in,hdivide={0.5in,*,0.75in},vdivide={1in,7.25in,1in},papersize={7.5in,9.25in}]{geometry}"""

_PREAMBLE = r"""
\usepackage[]{geometry}
\geometry{bindingoffset=0.45in,textheight=7.25in,hdivide={0.5in,*,0.75in},vdivide={1in,7.25in,1in},papersize={7.5in,9.25in}}

%XeLaTeX packages
\usepackage{xltxtra}
\usepackage{fontspec} %Font package
\usepackage{xunicode}

%Select fonts
\setmainfont[Mapping=tex-text]{nimbusserif}
\setsansfont[Mapping=tex-text]{nimbussans}
\setmonofont{nimbusmono}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    filecolor=black,
    urlcolor=black
}
\fvset{frame=single,xleftmargin=9pt,numbersep=4pt}

\pagestyle{fancy}

% header and footer styles
\renewcommand{\chaptermark}[1]%
  {\markboth{\MakeUppercase{\thechapter.\ #1}}{}
  }
\renewcommand{\sectionmark}[1]%
  {\markright{\MakeUppercase{\thesection.\ #1}}
  }

% defaults for fancy style
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhf{}
\fancyfoot[C]{\thepage}

% plain style
\fancypagestyle{plain}{
  \renewcommand{\headrulewidth}{0pt} % ho header line
  \renewcommand{\footrulewidth}{0pt}% no footer line
  \fancyhf{} % empty header and footer
  \fancyfoot[C]{\thepage}
}

% title page styles
\makeatletter
\def\@subtitle{\relax}
\newcommand{\subtitle}[1]{\gdef\@subtitle{#1}}
\renewcommand{\maketitle}{
  \begin{titlepage}
    {\rm\Huge\@title\par}
    {\em\large\py@release\releaseinfo\par}
    \if\@subtitle\relax\else\large\@subtitle\par\fi
    {\large\@author\par}
  \end{titlepage}
}
\makeatother

% Redefine link and title colors
\definecolor{TitleColor}{rgb}{0,0,0}
\definecolor{InnerLinkColor}{rgb}{0.208,0.374,0.486}
\definecolor{OuterLinkColor}{rgb}{0.216,0.439,0.388}
% Redefine these colors to something not white if you want to have colored
% background and border for code examples.
\definecolor{VerbatimColor}{rgb}{1,1,1}
\definecolor{VerbatimBorderColor}{rgb}{1,1,1}

% icons in note and warning boxes
\usepackage{ifthen}

% Keep a copy of the original sphinxadmonition environment
\let\origbeginadmon\sphinxadmonition
\let\origendadmon\endsphinxadmonition

% Redefine the sphinxadmonition environment so we can add our own code to it
\renewenvironment{sphinxadmonition}[2]{%
  \origbeginadmon{#1}{}% equivalent to original \begin{sphinxadmonition}{#1}{#2}
  % load graphics
  \ifthenelse{\equal{#1}{warning}}{\includegraphics{latex-warning.png}}{}
  \ifthenelse{\equal{#1}{note}}{\includegraphics{latex-note.png}}{}
  % etc.
  }{%
\origendadmon % equivalent to original \end{sphinxadmonition}
}

% try to prevent code-block boxes from splitting across pages
\sloppy
\widowpenalty=300
\clubpenalty=300
\setlength{\parskip}{3ex plus 2ex minus 2ex}

% suppress page numbers on pages showing part title
\makeatletter
\let\sv@endpart\@endpart
\def\@endpart{\thispagestyle{empty}\sv@endpart}
\makeatother

% prevent page numbers in TOC (reset to fancy by frontmatter directive)
\pagestyle{empty}
"""

latex_elements = {
    'preamble': _PREAMBLE,
    'releasename': 'Version',
    'title': r'The Pyramid Web Framework',
#    'pointsize':'12pt', # uncomment for 12pt version
}

# secnumdepth counter reset to 2 causes numbering in related matter;
# reset to -1 causes chapters to not be numbered, reset to -2 causes
# parts to not be numbered.

#part	      -1
#chapter       0
#section       1
#subsection    2
#subsubsection 3
#paragraph     4
#subparagraph  5


class FrontMatter(Directive):
    def run(self):
        return [nodes.raw(
            '',
            format='latex')]


class MainMatter(Directive):
    def run(self):
        return [nodes.raw(
            '',
            format='latex')]


class BackMatter(Directive):
    def run(self):
        return [nodes.raw(
            '',
            format='latex')]


def app_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    """custom role for :app: marker, does nothing in particular except allow
    :app:`Pyramid` to work (for later search and replace)."""
    if 'class' in options:
        assert 'classes' not in options
        options['classes'] = options['class']
        del options['class']
    return [nodes.inline(rawtext, utils.unescape(text), **options)], []


def setup(app):
    app.add_role('app', app_role)
    app.add_directive('frontmatter', FrontMatter)
    app.add_directive('mainmatter', MainMatter)
    app.add_directive('backmatter', BackMatter)
    app.connect('autodoc-process-signature', resig)


def resig(app, what, name, obj, options, signature, return_annotation):
    """ Allow for preservation of ``@action_method`` decorated methods
    in configurator """
    docobj = getattr(obj, '__docobj__', None)
    if docobj is not None:
        argspec = inspect.getargspec(docobj)
        if argspec[0] and argspec[0][0] in ('cls', 'self'):
            del argspec[0][0]
        signature = inspect.formatargspec(*argspec)
    return signature, return_annotation

# turn off all line numbers in latex formatting

## from pygments.formatters import LatexFormatter
## from sphinx.highlighting import PygmentsBridge

## class NoLinenosLatexFormatter(LatexFormatter):
##     def __init__(self, **options):
##         LatexFormatter.__init__(self, **options)
##         self.linenos = False

## PygmentsBridge.latex_formatter = NoLinenosLatexFormatter

# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = 'The Pyramid Web Framework, Version %s' \
             % release
epub_author = 'Chris McDonough'
epub_publisher = 'Agendaless Consulting'
epub_copyright = '2008-%d' % thisyear

# The language of the text. It defaults to the language option
# or en if the language is not set.
epub_language = 'en'

# The scheme of the identifier. Typical schemes are ISBN or URL.
epub_scheme = 'ISBN'

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = '0615445675'

# A unique identification for the text.
epub_uid = 'The Pyramid Web Framework, Version %s' \
           % release

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['_static/opensearch.xml', '_static/doctools.js',
    '_static/jquery.js', '_static/searchtools.js', '_static/underscore.js',
    '_static/basic.css', 'search.html', '_static/websupport.js']


# The depth of the table of contents in toc.ncx.
epub_tocdepth = 3

# For a list of all settings, visit http://sphinx-doc.org/config.html

# -- Options for linkcheck builder -------------------------------------------

# List of items to ignore when running linkcheck
linkcheck_ignore = [
    r'http://localhost:\d+',
    r'http://localhost',
    r'https://webchat.freenode.net/#pyramid',  # JavaScript "anchor"
]
