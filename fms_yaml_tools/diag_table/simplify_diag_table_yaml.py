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

from os import path, strerror
import errno
import yaml
import click
from .. import __version__


@click.command()
@click.argument("diag_table_yaml")
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the conversion")
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="diag_table.yaml",
              help="Path to the output diag table yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.version_option(__version__, "--version")
def simplify_diag_yaml(diag_table_yaml, output_yaml, debug, force_write):
    verboseprint = print if debug else lambda *a, **k: None
    if not path.exists(diag_table_yaml):
        raise FileNotFoundError(errno.ENOENT,
                                strerror(errno.ENOENT),
                                diag_table_yaml)

    try:
        verboseprint("Opening on the diag_table yaml:" + diag_table_yaml)
        with open(diag_table_yaml) as fl:
            verboseprint("Parsing the diag_table yaml:" + diag_table_yaml)
            my_table = yaml.safe_load(fl)
            simplify_diag_file(my_table)
    except yaml.scanner.ScannerError as scanerr:
        print("ERROR:", scanerr)
        raise Exception("ERROR: Please verify that the previous entry in the yaml file is entered as "
                        "\"key: value\" and not as \"key:value\" ")

    if isinstance(my_table, str):
        raise Exception("ERROR: diagYaml contains incorrectly formatted key value pairs."
                        " Make sure that entries are formatted as \"key: value\" and not \"key:value\" ")

    out_file_op = "x"  # Exclusive write
    if force_write:
        out_file_op = "w"

    with open(output_yaml, out_file_op) as myfile:
        yaml.dump(my_table, myfile, sort_keys=False)


def simplify_diag_file(my_table):
    if "diag_files" not in my_table:
        raise Exception("Your diag_table yaml does not have any diag_files defined.")

    diag_files = my_table["diag_files"]
    for diag_file in diag_files:
        if "varlist" not in diag_file:
            raise Exception("Your diag_table yaml does not have any diag_files defined.")

        diag_fields = diag_file["varlist"]
        reduction = []
        kind = []
        for diag_field in diag_fields:
            reduction.append(diag_field["reduction"])
            kind.append(diag_field["kind"])
        common_reduction = max(set(reduction), key=reduction.count)
        common_kind = max(set(kind), key=kind.count)

        diag_file["reduction"] = common_reduction
        diag_file["kind"] = common_kind
        for diag_field in diag_fields:
            if diag_field["reduction"] == common_reduction:
                del diag_field["reduction"]
            if diag_field["kind"] == common_kind:
                del diag_field["kind"]


if __name__ == "__main__":
    simplify_diag_yaml(prog_name="simplify_diag_yaml")
