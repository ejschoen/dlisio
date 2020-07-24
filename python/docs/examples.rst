A quick guide
=============

This is a quick guide to get you started with dlisio. Note that all classes and
functions are more thoroughly documented under :ref:`apiref`. Please refer
there for more information about them.

The same documentation is also available directly in your favorite python
interpreter and in the unix console, just type :code:`help(function)` or  :code:`pydoc
function`, respectably. In the interpreter, help can be used directly on
class instances. E.g: :code:`help(frame)` or :code:`help(frame.curves)`

Opening files
-------------

Load all :ref:`Logical files`:

.. code-block:: python

    >>> with dlisio.load(filename) as files:
    ...     for f in files:
    ...         pass

The returned :code:`files` can be iterated over and operations can be applied
to each logical file.

If you only want to work with one logical file at the time,
:py:func:`dlisio.load()` supports automatic unpacking of logical files. The
following syntax unpacks the first logical file into :code:`f` and stores the
rest (0-n) logical files into :code:`*tail`.


.. code-block:: python

    >>> with dlisio.load(filename) as (f, *tail):
    ...     pass

Or, if the number of logical files is known:

.. code-block:: python

    >>> with dlisio.load(filename) as (f1, f2, f3):
    ...     pass

When a file is loaded, you can output some basic information about the physical
file:

.. code-block:: python

    >>> import dlisio
    >>> with dlisio.load(filename) as files:
    ...     files.describe()
    ----------------------
    Batch of Logical Files
    ----------------------
    Number of Logical Files : 3

    Description : dlis(DDBC1)
    Frames      : 0
    Channels    : 0

    Description : dlis(DDBC2)
    Frames      : 2
    Channels    : 22

    Description : dlis(DDBC3)
    Frames      : 2
    Channels    : 160

Or about a logical file:

.. code-block:: python

    >>> import dlisio
    >>> with dlisio.load(filename) as (f, *tail):
    ...     f.describe()
    ------------
    Logical File
    ------------
    Description  : dlis(MSCT_200LTP)
    Frames       : 2
    Channels     : 104

    Known objects
    --
    FILE-HEADER             : 1
    ORIGIN                  : 3
    CALIBRATION-COEFFICIENT : 8
    CHANNEL                 : 104
    FRAME                   : 2

    Unknown objects
    --
    440-CHANNEL             : 93
    440-OP-CORE_TABLES      : 17
    440-OP-CHANNEL          : 101

Accessing objects
-----------------

Think of :ref:`Logical files` as pools of objects with different types.  All
objects of a type can be reached by name, e.g. channels or coefficients:

.. code-block:: python

    >>> for ch in f.channels:
    ...     pass

See :ref:`Logical files` for a full list of all object types.

:py:func:`dlisio.dlis.object` lets you access a specific object:

.. code-block:: python

    >>> obj = f.object('CHANNEL', 'TDEP')

Objects can also be searched for with :py:func:`dlisio.dlis.match()`:

.. code-block:: python

    >>> objs = f.match('T.*')

Inspect an object with the :code:`.describe()`-method:

.. code-block:: python

    >>> obj.describe()
    -----
    Frame
    -----
    name   : 800T
    origin : 2
    copy   : 0

    Channel indexing
    --
    Indexed by       : TIME
    Interval         : [33354518, 35194520]
    Direction        : INCREASING
    Constant spacing : 800
    Index channel    : Channel(TIME)

    Channels
    --
    TIME TDEP ETIM LMVL UMVL CFLA OCD  RCMD RCPP CMRT
    RCNU DCFL DFS  DZER RHMD HMRT RHV  RLSW MNU  S1CY
    S2CY RSCU RSTS UCFL CARC CMDV CMPP CNU  HMDV HV
    LSWI SCUR SSTA RCMP RHPP RRPP CMPR HPPR RPPV SMSC
    CMCU HMCU CMLP

Frames and Channels
-------------------

See :ref:`Curves` for information about the relationship between Channels and
Frames. Have a look at :ref:`Channel` and :ref:`Frame`, they contain some
useful metadata in addition to the curve-values!

Channels belonging to a Frame can be accessed directly through
:py:attr:`dlisio.plumbing.Frame.channels`:

.. code-block:: python

    >>> frame.channels[0]
    Channel(TDEP)

Likewise, the parent-frame of a Channel can be accessed through the channel:

.. code-block:: python

    >>> ch.frame
    Frame(800T)

The actual curve data of a Channel is accessed by :py:func:`dlisio.plumbing.Channel.curves()`,
which returns a structured numpy array that support common slicing operations:

.. code-block:: python

    >>> curve = ch.curves()
    >>> curve[0:5]
    array([852606., 852606., 852606., 852606., 852606.], dtype=float32)

Note that its almost always considerably faster to read curves-data with
:py:func:`dlisio.plumbing.Frame.curves()`. Please refer to
:py:func:`dlisio.plumbing.Channel.curves()` for further elaboration on why this
is.

Access all curves in a frame with :py:func:`dlisio.plumbing.Frame.curves()`.
The returned structured numpy array can be indexed by Channel mnemonics
and/or sliced by samples:

.. code-block:: python

    >>> curves = fr.curves()
    >>> curves[[fr.index, 'TENS_SL']][0:5]
    array([(16677259., 2233.), (16678259., 2237.), (16679259., 2211.),
           (16680259., 2193.), (16681259., 2213.)])

Note that double brackets are needed in order to access muliple channels at
once.

As long as the frame only contains channels with scalar samples, it can be
trivially converted to a pandas DataFrame:

.. code-block:: python

    >>> import pandas as pd
    >>> curves = pd.DataFrame(frame.curves())

For more examples of how to work with the curve-data, please refer to
:py:func:`dlisio.plumbing.Frame.curves()` and :py:func:`dlisio.plumbing.Channel.curves()`
