"""
Production Schema Registry & Backward Compatibility Verifier.
Phase 7: Schema Registry.
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.SchemaRegistry")


class SchemaDefinition(BaseModel):
    schema_id: str
    schema_type: str  # "event", "feature", "model_input", "api_response"
    version: str      # Semantic version e.g. "v1.0", "v2.0"
    fields: Dict[str, str]  # field_name -> expected_type (e.g. "float", "string", "int", "datetime")
    required_fields: List[str]
    description: str = ""
    created_at: str = Field(default_factory=lambda: "2026-09-03T00:00:00Z")


class SchemaRegistry:
    """Central repository for schema versioning, field requirements, and backward compatibility validation."""

    def __init__(self):
        self._schemas: Dict[str, SchemaDefinition] = {}
        self._bootstrap_standard_schemas()

    def _bootstrap_standard_schemas(self):
        # 1. Event schemas
        self.register_schema(
            SchemaDefinition(
                schema_id="market:trade:v2.0",
                schema_type="event",
                version="v2.0",
                fields={"price": "float", "quantity": "float", "side": "string", "trade_id": "string", "timestamp": "datetime"},
                required_fields=["price", "quantity", "side", "trade_id"],
                description="Canonical trade event schema"
            )
        )
        self.register_schema(
            SchemaDefinition(
                schema_id="market:orderbook:v2.0",
                schema_type="event",
                version="v2.0",
                fields={"mid_price": "float", "spread_bps": "float", "microprice": "float", "imbalance_10bps": "float"},
                required_fields=["mid_price", "spread_bps", "microprice"],
                description="Canonical orderbook depth snapshot"
            )
        )

        # 2. Feature schemas
        self.register_schema(
            SchemaDefinition(
                schema_id="features:core:v2.0",
                schema_type="feature",
                version="v2.0",
                fields={
                    "spread_bps": "float",
                    "microprice": "float",
                    "order_imbalance": "float",
                    "realized_volatility_5m": "float",
                    "cvd_quote": "float",
                    "funding_rate": "float",
                    "basis_annualized": "float",
                    "liquidation_intensity": "float",
                    "trend_strength": "float"
                },
                required_fields=["spread_bps", "order_imbalance", "realized_volatility_5m", "funding_rate"],
                description="Core 9-factor real-time feature matrix"
            )
        )

        # 3. Model input schemas
        self.register_schema(
            SchemaDefinition(
                schema_id="model_input:champion:v2.0",
                schema_type="model_input",
                version="v2.0",
                fields={
                    "spread_bps": "float",
                    "microprice": "float",
                    "order_imbalance": "float",
                    "realized_volatility_5m": "float",
                    "cvd_quote": "float",
                    "funding_rate": "float"
                },
                required_fields=["spread_bps", "order_imbalance", "realized_volatility_5m", "funding_rate"],
                description="Input vector definition for production champion model"
            )
        )

        # 4. API response schema
        self.register_schema(
            SchemaDefinition(
                schema_id="api:signals:v2.0",
                schema_type="api_response",
                version="v2.0",
                fields={
                    "signal": "string",
                    "actionable": "bool",
                    "conviction_score": "float",
                    "p_up": "float",
                    "p_down": "float",
                    "p_neutral": "float"
                },
                required_fields=["signal", "actionable", "conviction_score", "p_up", "p_down"],
                description="Standard response schema for actionable signals"
            )
        )

    def register_schema(self, schema: SchemaDefinition):
        self._schemas[schema.schema_id] = schema
        logger.info(f"[SchemaRegistry] Registered {schema.schema_type} schema: {schema.schema_id}")

    def get_schema(self, schema_id: str) -> Optional[SchemaDefinition]:
        return self._schemas.get(schema_id)

    def validate_payload(self, schema_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payload against schema definition."""
        schema = self.get_schema(schema_id)
        if not schema:
            return {"valid": False, "error": f"Schema {schema_id} not registered"}

        missing = [f for f in schema.required_fields if f not in payload or payload[f] is None]
        if missing:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing}",
                "missing_fields": missing
            }

        # Type checks
        type_mismatches = []
        for field, exp_type in schema.fields.items():
            if field in payload and payload[field] is not None:
                val = payload[field]
                if exp_type == "float" and not isinstance(val, (int, float)):
                    type_mismatches.append(f"{field}: expected float, got {type(val).__name__}")
                elif exp_type == "int" and not isinstance(val, int):
                    type_mismatches.append(f"{field}: expected int, got {type(val).__name__}")
                elif exp_type == "string" and not isinstance(val, str):
                    type_mismatches.append(f"{field}: expected str, got {type(val).__name__}")
                elif exp_type == "bool" and not isinstance(val, bool):
                    type_mismatches.append(f"{field}: expected bool, got {type(val).__name__}")

        if type_mismatches:
            return {
                "valid": False,
                "error": f"Type mismatches: {type_mismatches}",
                "type_errors": type_mismatches
            }

        return {"valid": True, "schema_id": schema_id}

    def check_backward_compatibility(
        self,
        base_schema_id: str,
        new_schema: SchemaDefinition
    ) -> Dict[str, Any]:
        """Verify that new schema does not drop existing required fields or introduce breaking type mutations."""
        base_schema = self.get_schema(base_schema_id)
        if not base_schema:
            return {"compatible": True, "note": "New independent schema lineage"}

        breaking_changes = []
        # Check required fields retention
        for req in base_schema.required_fields:
            if req not in new_schema.fields:
                breaking_changes.append(f"Previously required field '{req}' was removed.")

        # Check existing field types
        for f, t in base_schema.fields.items():
            if f in new_schema.fields and new_schema.fields[f] != t:
                breaking_changes.append(
                    f"Field '{f}' changed type from '{t}' to '{new_schema.fields[f]}'."
                )

        if breaking_changes:
            return {
                "compatible": False,
                "breaking_changes": breaking_changes,
                "error": "Backward compatibility check failed."
            }

        return {"compatible": True, "breaking_changes": []}


schema_registry = SchemaRegistry()
