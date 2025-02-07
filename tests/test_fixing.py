import os
import shutil
import tempfile
from pathlib import Path

import pytest

from fortran_linter.cli import main

HERE = Path(__name__).parent.absolute()


class TestAutoFixing:
    WDIR = None
    OWDIR = None
    test_file = None
    reference_file = None

    def setup(self):
        self.WDIR = tempfile.mkdtemp()
        source_file = HERE / "tests" / "test.f90"
        reference_file = HERE / "tests" / "test_reference.f90"
        shutil.copy2(source_file, self.WDIR)
        shutil.copy2(reference_file, self.WDIR)

        self.test_file = Path(self.WDIR) / "test.f90"
        self.reference_file = Path(self.WDIR) / "test_reference.f90"

    def test_fail_with_error(self):
        with pytest.raises(SystemExit):
            main([str(self.test_file), "--stdout"])

    def test_autofix(self):
        with pytest.raises(SystemExit):
            main([str(self.test_file), "-i"])
        expected = self.reference_file.read_text()
        obtained = self.test_file.read_text()

        for lexp, lobt in zip(expected.split(), obtained.split()):
            assert lexp == lobt

    def test_autofix_folder(self):
        with pytest.raises(SystemExit):
            main([self.WDIR, "-i"])

        expected = self.reference_file.read_text()
        obtained = self.test_file.read_text()

        for lexp, lobt in zip(expected.split(), obtained.split()):
            assert lexp == lobt

    def test_autofix_folder_or_dile_do_not_exists(self):
        not_a_folder = self.WDIR
        # this wile continue to append "subdir" to the working directory
        # until the directory do not exists
        while os.path.exists(not_a_folder) and os.path.isdir(not_a_folder):
            not_a_folder = os.path.join(not_a_folder, "subdir")

        with pytest.raises(FileNotFoundError):
            main([not_a_folder, "--stdout"])

        # if the folder not exists also this file
        not_a_file = os.path.join(not_a_folder, "whatever.f90")

        with pytest.raises(FileNotFoundError):
            main([not_a_file, "--stdout"])

    def tearDown(self):
        pass
