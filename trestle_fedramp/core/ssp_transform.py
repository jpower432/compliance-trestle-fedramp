# Copyright (c) 2024 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Populate FedRAMP Template."""

import pathlib

from pkg_resources import resource_filename

from trestle.common.err import TrestleError

from trestle_fedramp.const import (FEDRAMP_APPENDIX_A_HIGH, FEDRAMP_APPENDIX_A_LOW, FEDRAMP_APPENDIX_A_MODERATE)
from trestle_fedramp.core.ssp_reader import FedrampSSPData, FedrampSSPReader


class BaselineLevel:
    """Represents the baseline level for the FedRAMP SSP."""

    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'

    LEVELS = {LOW, MODERATE, HIGH}

    @classmethod
    def get_template(cls, level: str) -> str:
        """Get the template file for the given level.

        Args:
            level (str): The baseline level ('low', 'moderate', 'high').

        Returns:
            str: The file path of the template.
        """
        resources_path = 'trestle_fedramp.resources'
        data = {
            cls.LOW: resource_filename(resources_path, FEDRAMP_APPENDIX_A_LOW),
            cls.MODERATE: resource_filename(resources_path, FEDRAMP_APPENDIX_A_MODERATE),
            cls.HIGH: resource_filename(resources_path, FEDRAMP_APPENDIX_A_HIGH)
        }
        if level not in cls.LEVELS:
            raise ValueError(f'Invalid level: {level}. Use one of {cls.LEVELS}')
        return data[level]


class FedrampSSPTransformer:
    """Populate FedRAMP Template with SSP Information."""

    def __init__(self, trestle_root: pathlib.Path, baseline_level: str) -> None:
        """Initialize FedRAMP SSP Converter."""
        # Set initial template
        self.template = pathlib.Path(BaselineLevel.get_template(baseline_level)).resolve()

        if not self.template.exists():
            raise TrestleError(f'FedRAMP Template {self.template} does not exist')

        self.trestle_root = trestle_root

    def transform(self, ssp_file_path: pathlib.Path, output_file: pathlib.Path) -> None:
        """Populate FedRAMP SSP Appendix A template with OSCAL SSP information."""
        ssp_reader = FedrampSSPReader(trestle_root=self.trestle_root)
        _: FedrampSSPData = ssp_reader.read_ssp_data(ssp_file_path)
        # The data from the SSP file
        # Loop the template filling in the data for each control
        # Save the populated template to the output file
        raise NotImplementedError

    def _set_control_origination(self, control_id: str, origination: str) -> None:
        """Set the control origination value."""
        raise NotImplementedError
