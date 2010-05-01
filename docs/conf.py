# -*- coding: utf-8 -*-
#
# repoze.bfg documentation build configuration file, created by
# sphinx-quickstart on Wed Jul 16 13:18:14 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import sys, os

# skip raw nodes
from sphinx.writers.text import TextTranslator
from docutils import nodes
def raw(*arg):
    raise nodes.SkipNode
TextTranslator.visit_raw = raw

book = os.environ.get('BOOK')

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
parent = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.abspath(parent))
wd = os.getcwd()
os.chdir(parent)
os.system('%s setup.py test -q' % sys.executable)
os.chdir(wd)

for item in os.listdir(parent):
    if item.endswith('.egg'):
        sys.path.append(os.path.join(parent, item))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['.templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'The repoze.bfg Web Application Framework'
copyright = '2008-2010, Agendaless Consulting'

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = '1.3a3'
# The full version, including alpha/beta/rc tags.
release = version

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directories, that shouldn't be searched
# for source files.
#exclude_dirs = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = book and 'bw' or 'sphinx'

# Options for HTML output
# -----------------------

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
html_style = 'repoze.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = 'The repoze.bfg Web Application Framework v%release%'

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (within the static path) to place at the top of
# the sidebar.
html_logo = '.static/logo_hi.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['.static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/<name>.
#html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'repozebfg'

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('latexindex', 'repozebfg.tex', 'The repoze.bfg Web Application Framework',
   'Chris McDonough', 'manual'),
    ]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = '.static/logo_hi.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_use_parts = True

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
latex_use_modindex = False

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

\makeatletter
\renewcommand{\py@noticestart@warning}{\py@heavybox}
\renewcommand{\py@noticeend@warning}{\py@endheavybox}
\renewcommand{\py@noticestart@note}{\py@heavybox}
\renewcommand{\py@noticeend@note}{\py@endheavybox}
\makeatother

% icons in note and warning boxes
\usepackage{ifthen}
% Keep a copy of the original notice environment
\let\origbeginnotice\notice
\let\origendnotice\endnotice

% Redefine the notice environment so we can add our own code to it
\renewenvironment{notice}[2]{%
  \origbeginnotice{#1}{}% equivalent to original \begin{notice}{#1}{#2}
  % load graphics
  \ifthenelse{\equal{#1}{warning}}{\includegraphics{exclaim.png}}{}
  \ifthenelse{\equal{#1}{note}}{\includegraphics{info.png}}{}
  % etc.
}{%
  \origendnotice% equivalent to original \end{notice}
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
    'wrapperclass':'book',
    'date':'',
    'releasename':'Version',
    'title':r'The repoze.bfg Web Application \newline Framework',
#    'pointsize':'12pt', # uncomment for 12pt version
}

from docutils import nodes

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

def frontmatter(name, arguments, options, content, lineno,
                content_offset, block_text, state, state_machine):
    return [nodes.raw(
        '',
        r"""
\frontmatter
% prevent part/chapter/section numbering
\setcounter{secnumdepth}{-2}
% suppress headers
\pagestyle{plain}
% reset page counter
\setcounter{page}{1}
% suppress first toc pagenum
\addtocontents{toc}{\protect\thispagestyle{empty}} 
""",
        format='latex')]

def mainmatter(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    return [nodes.raw(
        '',
        r"""
\mainmatter
% allow part/chapter/section numbering
\setcounter{secnumdepth}{2}
% get headers back
\pagestyle{fancy} 
\fancyhf{}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\thepage}
\fancyhead[RO]{\rightmark}
\fancyhead[LE]{\leftmark}
""",
        format='latex')]

def backmatter(name, arguments, options, content, lineno,
              content_offset, block_text, state, state_machine):
    return [nodes.raw('', '\\backmatter\n\\setcounter{secnumdepth}{-1}\n',
                      format='latex')]

def setup(app):
    app.add_directive('frontmatter', frontmatter, 1, (0, 0, 0))
    app.add_directive('mainmatter', mainmatter, 1, (0, 0, 0))
    app.add_directive('backmatter', backmatter, 1, (0, 0, 0))

# strip "repoze.bfg." from all inline literals

from sphinx.writers.latex import LaTeXTranslator

def visit_literal(self, node):
        self.no_contractions += 1
        content = self.encode(node.astext().strip())
        self.no_contractions -= 1
        if self.in_title:
            self.body.append(r'\texttt{%s}' % content)
        elif node.has_key('role') and node['role'] == 'samp':
            self.body.append(r'\samp{%s}' % content)
        else:
            # XXX special treatment of overlong ``repoze.bfg.foo``
            # literals.
            if 'repoze.bfg.' in content:
                content = content.replace('repoze.bfg.', '')
            self.body.append(r'\code{%s}' % content)
        raise nodes.SkipNode
    
LaTeXTranslator.visit_literal = visit_literal

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
epub_title = 'The repoze.bfg Web Application Framework, Version 1.3'
epub_author = 'Chris McDonough'
epub_publisher = 'Agendaless Consulting'
epub_copyright = '2008-2010'

# The language of the text. It defaults to the language option
# or en if the language is not set.
epub_language = 'en'

# The scheme of the identifier. Typical schemes are ISBN or URL.
epub_scheme = 'ISBN'

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = '0615345379'

# A unique identification for the text.
epub_uid = 'The repoze.bfg Web Application Framework, Version 1.3-v0'

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
#epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
epub_tocdepth = 3
