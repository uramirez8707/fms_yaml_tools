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

import click
import importlib.resources
from fms_yaml_tools.schema.validate_schema import validate_yaml
import sys


@click.command()
# Debug is used to print more information to the screen.
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the validation")
# This option controls whether or not the program prints a success message
@click.option('--success/--no-show-success', type=click.BOOL, show_default=True, default=False,
              help="Print success message")
# This is the path to the file to be validated
@click.argument("ypath")
def validate_diag_yaml(ypath, debug, success):
    """ Validates a diag_table.yaml based on a schema to check for any errors. \n
        YPATH - Path to the diag_table.yaml file to be validated against the schema \n
    """
    schema_path = importlib.resources.files('fms_yaml_tools') / "schema/gfdl_msd_schemas/FMS/diag_table.json"
    errors, yaml_output = validate_yaml(ypath, schema_path, debug, success, yaml_version="diag")
    if not dump_out_error_messages(errors, yaml_output):
        sys.exit(f"\nERROR: {ypath} is not a valid yaml")


def clean_error(err, file_name):
    """
    This code updates the generic error message 'not valid under any of the given schemas'
    """
    if file_name is not None:
        if "not valid under any of the given schemas" in err:
            return ("is not valid under any of the given schemas. Check your entry. "
                    "Ensure all of the required keys are present!")
    return err


def parse_diag_error_message(err, y):
    """
    Parses a schema errors by including the name of the diag_file or the variable name.
    """
    path = list(err.absolute_path)
    msg = ""
    file_name = None
    if len(path) >= 2 and path[0] == "diag_files":
        file_idx = path[1]
        try:
            file_name = y["diag_files"][file_idx].get("file_name", f"index {file_idx}")
            msg += f" in diag_file '{file_name}'"
            if len(path) >= 4 and path[2] == "varlist":
                var_idx = path[3]
                var_name = y["diag_files"][file_idx]["varlist"][var_idx].get("var_name", f"index {var_idx}")
                msg += f", variable '{var_name}'"
        except (IndexError, KeyError, TypeError):
            pass

    failed_prop = path[-1] if path else "root"

    return f"Error-{failed_prop}: {msg} - {clean_error(err.message, file_name)}"


def dump_out_error_messages(errors, y):
    errors_out = []
    for i, err in enumerate(errors, 1):
        errors_out.append(parse_diag_error_message(err, y))
    if errors_out:
        print("The schema has the following error messages:")
        for i, err in enumerate(errors_out, start=1):
            print(f"{i}. {err}")
        return False
    return True


if __name__ == "__main__":
    validate_diag_yaml(prog_name="validate_diag_yaml")
