#!/usr/bin/env python3
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML
# * tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public License
# * as published by the Free Software Foundation, either version 3 of the
# * License, or (at your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but
# * WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

import unittest
import tempfile
import os
import pathlib
import yaml
from contextlib import contextmanager
from click.testing import CliRunner
from fms_yaml_tools.diag_table.diag_table_to_yaml import diag_to_yaml
from utils.test_constants import DIAG_TABLE_SAMPLE1, DIAG_TABLE_SAMPLE1_YAML


@contextmanager
def create_directory(tmp_path: pathlib.Path):
    """Set the cwd to the path

    Args:
        tmp_path (Path): The path to use

    Yields:
        None
    """
    origin = pathlib.Path().absolute()
    try:
        os.chdir(tmp_path)
        yield
    finally:
        os.chdir(origin)


class TestDiagTableToYaml(unittest.TestCase):
    def test_diag_table_to_yaml_cli(self):
        self.run_cli_test(DIAG_TABLE_SAMPLE1, DIAG_TABLE_SAMPLE1_YAML)

    def run_cli_test(self, diag_table, reference):
        with tempfile.TemporaryDirectory() as testdir:
            with create_directory(testdir):
                pathlib.Path("diag_table").write_text(diag_table)

                runner = CliRunner()
                result = runner.invoke(diag_to_yaml, ["diag_table", "--is-segment"])
                assert result.exit_code == 0

                output_file = pathlib.Path("diag_table.yaml")
                self.assertTrue(
                    output_file.exists(),
                    msg="Expected output file diag_table.yaml was not created.",
                )

                yaml_contents = yaml.safe_load(output_file.read_text())
                self.assertEqual(yaml_contents, reference)
