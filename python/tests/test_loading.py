"""
Testing general loading functionality
"""

import pytest

import shutil
import os

import dlisio

def test_filehandles_closed(tmpdir):
    # Check that we don't leak open filehandles
    #
    # This test uses the fact that os.remove fails on windows if the file is in
    # use as a proxy for testing that dlisio doesn't leak filehandles.  From the
    # python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sense on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test file to a tmpdir in order to make this test reliable.
    tmp = str(tmpdir.join('206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'))
    shutil.copyfile('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', tmp)

    many_logical = str(tmpdir.join('many_logical'))
    shutil.copyfile('data/chap4-7/many-logical-files.dlis', many_logical)

    with dlisio.load(tmp) as _:
        pass

    with dlisio.load(many_logical) as fls:
        assert len(fls) == 3

    os.remove(tmp)
    os.remove(many_logical)

def test_filehandles_closed_when_load_fails(tmpdir):
    # Check that we don't leak open filehandles on failure
    #
    # This test uses the fact that os.remove fails on windows if the file is in
    # use as a proxy for testing that dlisio doesn't leak filehandles. From the
    # python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sense on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test files to a tmpdir in order to make this test reliable.
    findvrl = str(tmpdir.join('findvrl'))
    shutil.copyfile('data/chap2/nondlis.txt', findvrl)

    offsets = str(tmpdir.join('offsets'))
    shutil.copyfile('data/chap2/wrong-lrhs.dlis', offsets)

    extract = str(tmpdir.join('extract'))
    shutil.copyfile('data/chap2/padbytes-bad.dlis', extract)

    fdata = str(tmpdir.join('fdata'))
    shutil.copyfile('data/chap3/implicit/fdata-broken-obname.dlis', fdata)

    many_logical = str(tmpdir.join('many_logical'))
    shutil.copyfile('data/chap4-7/many-logical-files-error-in-last.dlis',
                    many_logical)

    # dlisio.load fails at findvrl
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(findvrl)

    # dlisio.load fails at core.findoffsets
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(offsets)

    # dlisio.load fails at core.stream.extract
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(extract)

    # dlisio.load fails at core.findfdata
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(fdata)

    # dlisio.load fails, but 1 LF was already processed successfully
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(many_logical)

    # If dlisio has properly closed the files, removing them should work.
    os.remove(findvrl)
    os.remove(offsets)
    os.remove(extract)
    os.remove(fdata)
    os.remove(many_logical)

def test_context_manager():
    path = 'data/chap4-7/many-logical-files.dlis'
    f, *_ = dlisio.load(path)
    _ = f.fileheader
    f.close()

    files = dlisio.load(path)
    for f in files:
        _ = f.fileheader
        f.close()

    f, *files = dlisio.load(path)
    _ = f.fileheader
    for g in files:
        _ = g.fileheader
        g.close()

def test_context_manager_with():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlisio.load(path) as (f, *_):
        _ = f.fileheader

    with dlisio.load(path) as files:
        for f in files:
            _ = f.fileheader

    with dlisio.load(path) as (f, *files):
        _ = f.fileheader
        for g in files:
            _ = g.fileheader

def test_load_nonexisting_file():
    with pytest.raises(OSError) as exc:
        _ = dlisio.load("this_file_does_not_exist.dlis")
    assert "this_file_does_not_exist.dlis : No such file" in str(exc.value)

@pytest.mark.xfail(strict=False)
def test_invalid_attribute_in_load():
    # Error in one attribute shouldn't prevent whole file from loading
    # This is based on common enough error in creation time property in
    # origin.
    # It loads just fine on python 3.5, but fails in higher versions
    path = 'data/chap4-7/invalid-date-in-origin.dlis'
    with dlisio.load(path):
        pass
