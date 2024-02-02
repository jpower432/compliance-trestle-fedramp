# -*- mode:python; coding:utf-8 -*-

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
"""Testing fedramp transform command functionality."""

import argparse
import pathlib
from typing import Tuple

from trestle_fedramp.commands.transform import SSPTransformCmd


def test_transform_ssp(tmp_path: pathlib.Path, tmp_trestle_dir_with_ssp: Tuple[pathlib.Path, str]) -> None:
    """Test Fedramp SSP transform command."""
    tmp_trestle_dir, ssp_name = tmp_trestle_dir_with_ssp
    args = argparse.Namespace(
        ssp_name=ssp_name, level='high', output_file=str(tmp_path), trestle_root=tmp_trestle_dir, verbose=1
    )
    rc = SSPTransformCmd()._run(args)
    assert rc != 0


def test_transform_invalid_trestle_root(tmp_path: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test fails with an invalid trestle root."""
    args = argparse.Namespace(
        ssp_name='test-ssp', level='high', output_file=str(tmp_path), trestle_root=tmp_path, verbose=1
    )
    rc = SSPTransformCmd()._run(args)
    assert rc != 0


def test_transform_missing_ssp(tmp_path: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test fails with a missing ssp."""
    args = argparse.Namespace(
        ssp_name='test-ssp', level='high', output_file=str(tmp_path), trestle_root=tmp_trestle_dir, verbose=1
    )
    rc = SSPTransformCmd()._run(args)
    assert rc != 0
