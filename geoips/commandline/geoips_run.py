"""GeoIPS CLI "run" command.

Runs the appropriate script based on the args provided.
"""
from glob import glob
from importlib import resources
from os.path import basename
from subprocess import call

from geoips.commandline.geoips_command import GeoipsExecutableCommand

class GeoipsRun(GeoipsExecutableCommand):
    """GeoipsRun Sub-Command for running process-workflows (procflows)."""
    subcommand_name = "run"
    subcommand_classes = []

    def add_arguments(self):
        self.subcommand_parser.add_argument(
            "pkg_name",
            type=str.lower,
            default="geoips",
            choices=self.plugin_packages,
            help="GeoIPS Package to run a script from."
        )
        self.subcommand_parser.add_argument(
            "script_name",
            type=str,
            default="abi.static.Visible.imagery_annotated.sh",
            help="Script to run from previously selected package."
        )

    def __call__(self, args):
        """Run the provided GeoIPS command.

        Parameters
        ----------
        args: Namespace()
            - The argument namespace to parse through
        """
        pkg_name = args.pkg_name
        script_name = args.script_name
        script_dir = str(resources.files(pkg_name) / "../tests/scripts")
        available_scripts = sorted(
            [
                basename(script_path) for script_path in \
                glob(f"{script_dir}/*.sh")
            ]
        )
        if script_name not in available_scripts:
            # File doesn't exist, raise an error for that.
            err_str = f"Script name: {script_name} doesn't exist under '{script_dir}. "
            err_str += "If you want to try again with this package, try one of these "
            err_str += f"scripts instead: \n {available_scripts}"
            self.subcommand_parser.error(err_str)
        script_path = f"{script_dir}/{script_name}"
        output = call(script_path, shell=True)
        return output