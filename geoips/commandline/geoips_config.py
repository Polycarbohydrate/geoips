"""GeoIPS CLI "config" command.

Various configuration-based commands for setting up your geoips environment.
"""

from os import listdir, environ
from os.path import abspath, join
import requests
import tarfile

from geoips.commandline.geoips_command import GeoipsCommand, GeoipsExecutableCommand


class GeoipsConfigInstall(GeoipsExecutableCommand):
    """Config Sub-Command Class for installing packages/data.

    Supports installation of packages and test data needed for testing and/or running
    your GeoIPS environment.
    """

    subcommand_name = "install"
    subcommand_classes = []

    @property
    def test_dataset_dict(self):
        """Dictionary mapping of GeoIPS Test Datasets.

        Mapping goes {"test_dataset_name": "test_dataset_url"}
        """
        if not hasattr(self, "_test_dataset_urls"):
            self._test_dataset_dict = {
                "test_data_viirs": "https://io.cira.colostate.edu/s/mQ2HbE2Js4E9rba/download/test_data_viirs.tgz",  # noqa
                "test_data_smap": "https://io.cira.colostate.edu/s/CezXWwXg4qR2b94/download/test_data_smap.tgz",  # noqa
                "test_data_scat": "https://io.cira.colostate.edu/s/HyHLZ9F8bnfcTcd/download/test_data_scat.tgz",  # noqa
                "test_data_sar": "https://io.cira.colostate.edu/s/snxx8S5sQL3AL7f/download/test_data_sar.tgz",  # noqa
                "test_data_noaa_aws": "https://io.cira.colostate.edu/s/fkiPS3jyrQGqgPN/download/test_data_noaa_aws.tgz",  # noqa
                "test_data_gpm": "https://io.cira.colostate.edu/s/LT92NiFSA8ZSNDP/download/test_data_gpm.tgz",  # noqa
                "test_data_fusion": "https://io.cira.colostate.edu/s/DSz2nZsiPMDeLEP/download/test_data_fusion.tgz",  # noqa
                "test_data_clavrx": "https://io.cira.colostate.edu/s/ACLKdS2Cpgd2qkc/download/test_data_clavrx.tgz",  # noqa
                "test_data_amsr2": "https://io.cira.colostate.edu/s/FmWwX2ft7KDQ8N9/download/test_data_amsr2.tgz",  # noqa
            }
        return self._test_dataset_dict

    @property
    def geoips_testdata_dir(self):
        """String path to GEOIPS_TESTDATA_DIR."""
        if not hasattr(self, "_geoips_testdata_dir"):
            self._geoips_testdata_dir = environ["GEOIPS_TESTDATA_DIR"]
        return self._geoips_testdata_dir

    def add_arguments(self):
        """Add arguments to the config-subparser for the Config Command."""
        self.subcommand_parser.add_argument(
            "test_dataset_name",
            type=str.lower,
            choices=list(self.test_dataset_dict.keys()),
            help="GeoIPS Test Dataset to Install.",
        )

    def __call__(self, args):
        """Run the `geoips config install <test_dataset_name>` command.

        Parameters
        ----------
        args: Namespace()
            - The argument namespace to parse through
        """
        test_dataset_name = args.test_dataset_name
        test_dataset_url = self.test_dataset_dict[test_dataset_name]
        if test_dataset_name in listdir(self.geoips_testdata_dir):
            print(
                f"Test dataset '{test_dataset_name}' already exists under "
                f"'{join(self.geoips_testdata_dir, test_dataset_name)}'. See that "
                "location for the contents of the test dataset."
            )
        else:
            print(
                f"Installing {test_dataset_name} test dataset. This may take a while..."
            )
            self.download_extract_test_data(test_dataset_url, self.geoips_testdata_dir)
            out_str = f"Test dataset '{test_dataset_name}' has been installed under "
            out_str += f"{self.geoips_testdata_dir}/{test_dataset_name}/"
            print(out_str)

    def download_extract_test_data(self, url, download_dir):
        """Download the specified URL and write it to the corresponding download_dir.

        Will extract the data using tarfile and create an archive by bundling the
        associated files and directories together.

        Parameters
        ----------
        url: str
            - The url of the test dataset to download
        download_dir: str
            - The directory in which to download and extract the data into
        """
        resp = requests.get(url, stream=True, timeout=15)
        if resp.status_code == 200:
            self.extract_data_cautiously(resp, download_dir)
        else:
            self.subcommand_parser.error(
                f"Error retrieving data from {url}; Status Code {resp.status_code}."
            )

    def extract_data_cautiously(self, response, download_dir):
        """Extract the GET Response cautiously and skip any dangerous members.

        Iterate through a Response and check that each member is not dangerous to
        extract to your machine. If it is, skip it.

        Where 'dangerous' is a filepath that is not part of 'download_dir'. File path
        maneuvering characters could be invoked ('../', ...), which we will not allow
        when downloading test data.

        Parameters
        ----------
        response: Requests Response Object
            - The GET Response from retrieving the data url
        download_dir: str
            - The directory in which to download and extract the data into
        """
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            # Validate and extract each member of the archive
            for m in tar:
                if not abspath(join(download_dir, m.name)).startswith(download_dir):
                    raise SystemExit("Found unsafe filepath in tar, exiting now.")
                tar.extract(m, path=download_dir)


class GeoipsConfig(GeoipsCommand):
    """Config top-level command for configuring your GeoIPS environment."""

    subcommand_name = "config"
    subcommand_classes = [GeoipsConfigInstall]
