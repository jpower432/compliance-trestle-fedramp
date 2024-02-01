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
"""Read and prepare OSCAL SSP information for template."""

import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional

from trestle.common.const import CONTROL_ORIGINATION, NAMESPACE_FEDRAMP
from trestle.common.list_utils import as_list
from trestle.common.load_validate import load_validate_model_path
from trestle.oscal.ssp import ImplementedRequirement, SystemSecurityPlan

from trestle_fedramp.const import (
    FEDRAMP_CUST_CONFIGURED,
    FEDRAMP_CUST_PROVIDED,
    FEDRAMP_HYBRID,
    FEDRAMP_INHERITED,
    FEDRAMP_SHARED,
    FEDRAMP_SP_CORPORATE,
    FEDRAMP_SP_SYSTEM
)


class ControlOrigination:
    """Represents the FedRAMP control origination mapping per FedRAMP validation rules."""

    SP_CORPORATE = 'sp-corporate'
    SP_SYSTEM = 'sp-system'
    CUST_CONFIGURED = 'customer-configured'
    CUST_PROVIDED = 'customer-provided'
    INHERITED = 'inherited'

    VALUES = {SP_SYSTEM, SP_CORPORATE, CUST_CONFIGURED, CUST_PROVIDED, INHERITED}

    @classmethod
    def get_long_name(cls, control_origination_values: List[str]) -> str:
        """
        Get the long name for control origination value(s).

        Args:
            control_origination_values: List of control origination values.

        Returns:
            Long name for the control origination value or combination of values.

        Notes:
            The input values can be a single or set control origination properties values.
            Any set with sp-corporate and sp-system is considered as hybrid and any set with customer
            and specific system is considered as shared.

        """
        data = {
            cls.SP_CORPORATE: FEDRAMP_SP_CORPORATE,
            cls.SP_SYSTEM: FEDRAMP_SP_SYSTEM,
            cls.CUST_CONFIGURED: FEDRAMP_CUST_CONFIGURED,
            cls.CUST_PROVIDED: FEDRAMP_CUST_PROVIDED,
            cls.INHERITED: FEDRAMP_INHERITED
        }
        if len(control_origination_values) > 1:
            for value in control_origination_values:
                cls._check_value(value)
            if cls.is_shared(control_origination_values):
                return FEDRAMP_SHARED
            if cls._is_hybrid(control_origination_values):
                return FEDRAMP_HYBRID
            raise ValueError(f'Invalid control origination values: {control_origination_values}')
        else:
            value = control_origination_values[0]
            cls._check_value(value)
            return data[value]

    @classmethod
    def _is_hybrid(cls, control_origination_values: List[str]) -> bool:
        """Check if the control origination values are hybrid."""
        return cls.SP_CORPORATE in control_origination_values and cls.SP_SYSTEM in control_origination_values

    @classmethod
    def is_shared(cls, control_origination_values: List[str]) -> bool:
        """Check if the control origination values are shared."""
        customer_sp: List[str] = [cls.CUST_CONFIGURED, cls.CUST_PROVIDED]
        provider_sp: List[str] = [cls.SP_CORPORATE, cls.SP_SYSTEM]

        # If the values contain both customer and provider values, then it is shared
        if set(control_origination_values).intersection(provider_sp) and set(control_origination_values).intersection(
                customer_sp):
            return True

        return False

    @classmethod
    def _check_value(cls, value: str) -> None:
        """Check if the value is valid."""
        if value not in cls.VALUES:
            raise ValueError(f'Invalid control origination value: {value}. Use one of {cls.VALUES}')


@dataclass
class FedrampSSPData:
    """Class to hold the OSCAL SSP data for FedRAMP SSP conversion."""

    control_origination_by_control: Dict[str, Optional[str]]


class FedrampSSPReader:
    """
    Read OSCAL SSP information for FedRAMP SSP conversion.

    Notes: This class provided an opinionated way to read the OSCAL SSP and
    prepare the data for the FedRAMP Template.
    """

    def __init__(self, trestle_root: pathlib.Path) -> None:
        """Initialize FedRAMP SSP reader."""
        self.trestle_root = trestle_root

    def read_ssp_data(self, ssp_path: pathlib.Path) -> FedrampSSPData:
        """Read the ssp from file and return the data for the FedRAMP Template."""
        data: FedrampSSPData = FedrampSSPData(control_origination_by_control={})
        ssp_data: SystemSecurityPlan = load_validate_model_path(self.trestle_root, ssp_path)  # type: ignore

        for implemented_requirement in as_list(ssp_data.control_implementation.implemented_requirements):
            control_id = implemented_requirement.control_id
            control_origination: Optional[str] = self._get_control_origination_values(implemented_requirement)
            data.control_origination_by_control[control_id] = control_origination
        return data

    def _get_control_origination_values(self, implemented_requirement: ImplementedRequirement) -> Optional[str]:
        """
        Check for the control origination property and return the value.

        Notes:
            This is checking for the FedRAMP specific property in the OSCAL SSP,
            not the OSCAL control origination values.
        """
        prop_values: List[str] = []
        if implemented_requirement.props:
            for prop in implemented_requirement.props:
                if prop.name == CONTROL_ORIGINATION and prop.ns == NAMESPACE_FEDRAMP:
                    prop_values.append(prop.value)

        if not prop_values:
            return None

        return ControlOrigination.get_long_name(prop_values)
