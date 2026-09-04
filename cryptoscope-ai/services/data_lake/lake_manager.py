"""
Data Lake Manager with Parquet, PyArrow, Polars, Manifests, and Checksums.
Phase 6: Data Lake Format.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from services.data_lake.storage_hierarchy import StorageTier, lake_hierarchy

logger = logging.getLogger("CryptoScope.LakeManager")


class LakeManager:
    """Manages writing and querying Parquet partitions with manifests and cryptographic checksums."""

    def __init__(self, hierarchy=lake_hierarchy):
        self.hierarchy = hierarchy

    def write_records_to_parquet(
        self,
        tier: StorageTier,
        provider: str,
        symbol: str,
        event_type: str,
        records: List[Dict[str, Any]],
        schema_version: str = "v2.0"
    ) -> Dict[str, Any]:
        """Write records to partitioned Parquet file with Snappy compression, SHA256, and manifest update."""
        if not records:
            return {"status": "EMPTY", "records_written": 0}

        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")

        partition_dir = self.hierarchy.get_partition_path(tier, provider, symbol, event_type, date_str, hour_str)

        # Convert to Polars DataFrame, flatten dict/list fields to JSON strings if needed
        sanitized_records = []
        for r in records:
            flat_rec = {}
            for k, v in r.items():
                if isinstance(v, (dict, list)):
                    flat_rec[k] = json.dumps(v, default=str)
                elif isinstance(v, datetime):
                    flat_rec[k] = v.isoformat()
                else:
                    flat_rec[k] = v
            sanitized_records.append(flat_rec)

        df = pl.DataFrame(sanitized_records)
        file_id = f"part_{int(now.timestamp() * 1000)}_{len(records)}.parquet"
        file_path = partition_dir / file_id

        # Write Parquet with PyArrow using Snappy compression
        arrow_table = df.to_arrow()
        pq.write_table(arrow_table, str(file_path), compression="snappy")

        # Compute SHA256 checksum
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        checksum = hasher.hexdigest()

        # Update partition manifest
        manifest_path = partition_dir / "manifest.json"
        manifest_entries = []
        if manifest_path.exists():
            try:
                with open(manifest_path, "r") as mf:
                    manifest_entries = json.load(mf)
            except Exception:
                manifest_entries = []

        manifest_entry = {
            "file_name": file_id,
            "tier": tier.value,
            "provider": provider.upper(),
            "symbol": symbol,
            "event_type": event_type,
            "record_count": len(records),
            "schema_version": schema_version,
            "written_at": now.isoformat(),
            "sha256": checksum,
            "file_size_bytes": os.path.getsize(file_path),
            "compression": "snappy"
        }
        manifest_entries.append(manifest_entry)

        with open(manifest_path, "w") as mf:
            json.dump(manifest_entries, mf, indent=2)

        logger.info(
            f"[LakeManager] Wrote {len(records)} records to {file_path.name} "
            f"({tier.value}) with sha256:{checksum[:12]}"
        )
        return manifest_entry

    def read_partition_polars(
        self,
        tier: StorageTier,
        provider: str,
        symbol: str,
        event_type: str,
        date_str: str,
        hour_str: str
    ) -> Optional[pl.DataFrame]:
        """Load partition into a Polars DataFrame."""
        partition_dir = self.hierarchy.get_partition_path(tier, provider, symbol, event_type, date_str, hour_str)
        parquet_files = list(partition_dir.glob("*.parquet"))
        if not parquet_files:
            return None
        dfs = [pl.read_parquet(str(f)) for f in parquet_files]
        return pl.concat(dfs) if len(dfs) > 1 else dfs[0]

    def verify_partition_integrity(
        self,
        tier: StorageTier,
        provider: str,
        symbol: str,
        event_type: str,
        date_str: str,
        hour_str: str
    ) -> Dict[str, Any]:
        """Verify checksums against partition manifest."""
        partition_dir = self.hierarchy.get_partition_path(tier, provider, symbol, event_type, date_str, hour_str)
        manifest_path = partition_dir / "manifest.json"
        if not manifest_path.exists():
            return {"status": "NO_MANIFEST", "verified_files": 0, "corrupted": []}

        with open(manifest_path, "r") as mf:
            manifest_entries = json.load(mf)

        corrupted = []
        verified = 0
        for entry in manifest_entries:
            fp = partition_dir / entry["file_name"]
            if not fp.exists():
                corrupted.append({"file": entry["file_name"], "reason": "FILE_MISSING"})
                continue
            hasher = hashlib.sha256()
            with open(fp, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calc_hash = hasher.hexdigest()
            if calc_hash != entry["sha256"]:
                corrupted.append({
                    "file": entry["file_name"],
                    "expected": entry["sha256"],
                    "calculated": calc_hash
                })
            else:
                verified += 1

        return {
            "status": "VALID" if not corrupted else "CORRUPTED",
            "verified_files": verified,
            "corrupted": corrupted
        }


lake_manager = LakeManager()
