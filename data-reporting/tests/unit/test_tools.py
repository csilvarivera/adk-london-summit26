# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from google.adk.tools import ToolContext
from app.tools import clean_missing_values, generate_and_save_chart


def test_clean_missing_values_success() -> None:
    """Tests clean_missing_values with standard data containing missing values."""
    raw_data = [
        {"Vendor": "Vendor_A", "Amount": 100, "Category": "IT"},
        {"Vendor": "Vendor_B", "Amount": 200, "Category": None},
        {"Vendor": None, "Amount": None, "Category": "HR"},
    ]
    raw_json = json.dumps(raw_data)

    result = clean_missing_values(raw_json)

    assert result["status"] == "success"
    cleaned = result["cleaned_data"]
    assert len(cleaned) == 3

    # Verification of median imputation for numeric columns:
    # Median of [100, 200] is 150.0
    assert cleaned[0]["Amount"] == 100
    assert cleaned[1]["Amount"] == 200
    assert cleaned[2]["Amount"] == 150.0

    # Verification of 'Unknown' imputation for non-numeric columns
    assert cleaned[0]["Category"] == "IT"
    assert cleaned[1]["Category"] == "Unknown"
    assert cleaned[2]["Vendor"] == "Unknown"


def test_clean_missing_values_invalid_json() -> None:
    """Tests clean_missing_values returns error status when JSON is malformed."""
    result = clean_missing_values("invalid json string {")
    assert result["status"] == "error"
    assert "message" in result


@pytest.mark.asyncio
async def test_generate_and_save_chart_fallback_local() -> None:
    """Tests generate_and_save_chart without ToolContext (saves local chart.png)."""
    # Clean up file if it exists prior to test
    if os.path.exists("chart.png"):
        os.remove("chart.png")

    data = [
        {"Vendor": "A", "Amount": 10},
        {"Vendor": "B", "Amount": 20},
    ]
    data_json = json.dumps(data)

    result = await generate_and_save_chart(
        data_json=data_json,
        chart_title="Test Local Chart",
        x_column="Vendor",
        y_column="Amount",
        chart_type="bar"
    )

    assert result["status"] == "success"
    assert "Successfully generated chart" in result["message"]
    assert result["artifact_name"] == "chart.png"
    assert os.path.exists("chart.png")

    # Clean up
    if os.path.exists("chart.png"):
        os.remove("chart.png")


@pytest.mark.asyncio
async def test_generate_and_save_chart_with_tool_context() -> None:
    """Tests generate_and_save_chart saving through a mocked ToolContext."""
    mock_context = MagicMock(spec=ToolContext)
    mock_context.save_artifact = AsyncMock(return_value=1) # mock version return

    data = [
        {"Vendor": "A", "Amount": 10},
        {"Vendor": "B", "Amount": 20},
    ]
    data_json = json.dumps(data)

    result = await generate_and_save_chart(
        data_json=data_json,
        chart_title="Test Context Chart",
        x_column="Vendor",
        y_column="Amount",
        chart_type="line",
        tool_context=mock_context
    )

    assert result["status"] == "success"
    assert result["artifact_name"] == "chart.png"
    assert result["version"] == 1
    assert "saved as session artifact 'chart.png'" in result["message"]

    # Verify that save_artifact was called
    mock_context.save_artifact.assert_called_once()
    args, kwargs = mock_context.save_artifact.call_args
    assert args[0] == "chart.png"


@pytest.mark.asyncio
async def test_generate_and_save_chart_missing_columns() -> None:
    """Tests generate_and_save_chart returning error status when columns are absent."""
    data = [
        {"Vendor": "A", "Amount": 10},
    ]
    data_json = json.dumps(data)

    result = await generate_and_save_chart(
        data_json=data_json,
        chart_title="Test Missing Column",
        x_column="NonExistentX",
        y_column="Amount",
        chart_type="bar"
    )

    assert result["status"] == "error"
    assert "not found in the dataset" in result["message"]
