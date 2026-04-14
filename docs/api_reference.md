# Nebula SDK API Reference

Welcome to the Nebula SDK API Reference. This document details the types and decorators available for developing plugins for NebulaLab Data Processor.

## `nebula_sdk.decorators`

### `register_operation(name, display_name=None, category="custom", params_schema=None, description=None)`
Decorator used to register a custom operation into the NebulaLab platform.

- **name** (`str`): Unique identifier for the operation.
- **display_name** (`str`, optional): Display name shown in the UI.
- **category** (`str`, optional): Grouping category in the UI (e.g., `preprocessing`, `analysis`, `custom`).
- **params_schema** (`Dict`, optional): Defines the input parameters the operation requires from the user.
- **description** (`str`, optional): Detailed description of what the operation does.

**Aliases:**
- `op`
- `register_operation_decorator`

---

## `nebula_sdk.types`

### `SampleProtocol`
A protocol class defining the interface of a single data sample accessible to the plugin.
- `active_data` (`pd.DataFrame`): The current state of the dataset in the data processing pipeline.
- `processed_data` (`pd.DataFrame | None`): The updated dataset set by an operation indicating it modified the data.

### `OperationContext`
Provides a higher-level API to interact with the sample, abstracting away underlying model updates.
- **`data`** -> `pd.DataFrame`: Returns a copy of the active data dataframe.
- **`update(df: pd.DataFrame)`** -> `OperationResult`: Replaces the sample's data with the updated DataFrame and returns a success result.
- **`compute(result: dict)`** -> `OperationResult`: Returns a computed metric without modifying the data itself.

---

## `nebula_sdk.models`

### `OperationResult`
Type Alias: `tuple[bool, dict[str, Any]]`

Every operation handler must return an `OperationResult`.
- The `bool` indicates whether the dataset was modified (`True`) or just a metric was computed/read (`False`).
- The `dict` can contain metadata like `{"status": "updated", "rows": ...}`.
