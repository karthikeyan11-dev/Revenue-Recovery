import logging
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger("app.integrations.vectorstore.chroma")

# Persistent ChromaDB storage path (configurable via CHROMA_PERSIST_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CHROMA_DIR = Path(os.environ.get("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db")))
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class RecoveryPlaybookService:
    """
    ChromaDB-backed Recovery Playbook Vector Store.
    Stores and retrieves historical resolved recovery cases for grounded RAG precedent reasoning.
    """

    _client: chromadb.ClientAPI | None = None
    _collection: Any | None = None
    COLLECTION_NAME: str = "recovery_playbook"

    @classmethod
    def get_client(cls) -> chromadb.ClientAPI:
        if cls._client is None:
            chroma_path = Path(
                os.environ.get("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db"))
            )
            chroma_path.mkdir(parents=True, exist_ok=True)
            cls._client = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return cls._client

    @classmethod
    def get_collection(cls) -> Any:
        if cls._collection is None:
            client = cls.get_client()
            cls._collection = client.get_or_create_collection(
                name=cls.COLLECTION_NAME,
                metadata={"description": "Historical resolved recovery cases precedent base"},
            )
        return cls._collection

    @classmethod
    def insert_resolved_case(
        cls,
        case_id: str,
        failure_reason: str,
        action_taken: str,
        channel: str | None,
        outcome: str,
        recovered_amount: float,
        segment: str | None = None,
    ) -> None:
        """
        Inserts or updates a resolved recovery case in ChromaDB recovery_playbook collection.
        """
        collection = cls.get_collection()
        chan = channel or "NONE"
        is_rec = bool(outcome.upper() in ["SUCCESS", "RECOVERED"])

        doc_text = (
            f"Failure Reason: {failure_reason} | "
            f"Action Taken: {action_taken} | Channel: {chan} | "
            f"Outcome: {outcome} | Recovered Amount: INR {recovered_amount:,.2f}"
        )

        metadata = {
            "case_id": str(case_id),
            "failure_reason": str(failure_reason),
            "action_taken": str(action_taken),
            "channel": str(chan),
            "outcome": str(outcome),
            "recovered_amount": float(recovered_amount),
            "is_recovered": is_rec,
        }
        if segment:
            metadata["segment"] = str(segment)

        try:
            collection.upsert(
                ids=[str(case_id)],
                documents=[doc_text],
                metadatas=[metadata],
            )
            logger.info(
                f"[ChromaDB:insert_resolved_case] Stored precedent case {case_id} (Reason: {failure_reason}, Outcome: {outcome})"
            )
        except Exception as e:
            logger.error(f"[ChromaDB:insert_resolved_case] Failed to store case {case_id}: {e}")

    @classmethod
    def query_similar_cases(
        cls,
        failure_reason: str,
        leak_type: str | None = None,
        segment: str | None = None,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieves the top k most similar historical resolved cases from ChromaDB.
        Returns list of case metadata dictionaries.
        """
        collection = cls.get_collection()
        total_count = collection.count()

        if total_count == 0:
            logger.info("[ChromaDB:query_similar_cases] recovery_playbook is empty (cold start).")
            return []

        query_text = (
            f"Failure Reason: {failure_reason} | "
            f"Leak Type: {leak_type or 'TRANSACTION_FAILURE'}"
        )

        n_results = min(k, total_count)

        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
            )

            retrieved: list[dict[str, Any]] = []
            if results and results.get("metadatas") and len(results["metadatas"]) > 0:
                for meta in results["metadatas"][0]:
                    retrieved.append(dict(meta))

            logger.info(
                f"[ChromaDB:query_similar_cases] Retrieved {len(retrieved)} cases for reason '{failure_reason}' (leak_type='{leak_type}')"
            )
            return retrieved

        except Exception as e:
            logger.error(f"[ChromaDB:query_similar_cases] Retrieval failed: {e}")
            return []

    @classmethod
    def get_playbook_count(cls) -> int:
        """Returns the total number of resolved cases stored in recovery_playbook."""
        collection = cls.get_collection()
        return collection.count()

    @classmethod
    def get_playbook_stats(cls) -> dict[str, Any]:
        """Returns knowledge accumulation stats and detailed breakdown for the recovery playbook."""
        collection = cls.get_collection()
        total_count = collection.count()
        if total_count == 0:
            return {
                "total_cases": 0,
                "baseline_precedents": 0,
                "learned_cases": 0,
                "failure_reasons": [],
                "outcomes": {"recovered_count": 0, "failed_or_escalated_count": 0},
                "actions": [],
            }

        try:
            records = collection.get(include=["metadatas"])
            metas = records.get("metadatas", []) or []
            learned = sum(1 for m in metas if str(m.get("case_id", "")).startswith("case_"))
            baseline = sum(1 for m in metas if str(m.get("case_id", "")).startswith("hist_"))

            from collections import Counter

            reason_counts = Counter(str(m.get("failure_reason", "UNKNOWN")) for m in metas)
            outcome_counts = Counter(str(m.get("outcome", "FAILED")).upper() for m in metas)
            action_counts = Counter(str(m.get("action_taken", "RETRY")) for m in metas)

            recovered_c = outcome_counts.get("RECOVERED", 0) + outcome_counts.get("SUCCESS", 0)
            failed_c = sum(
                v for k, v in outcome_counts.items() if k not in ["RECOVERED", "SUCCESS"]
            )

            reasons_list = [
                {
                    "failure_reason": r,
                    "display_name": r.replace("_", " ").title(),
                    "count": cnt,
                }
                for r, cnt in reason_counts.most_common()
            ]

            actions_list = [
                {
                    "action": a,
                    "display_name": a.replace("_", " ").title(),
                    "count": cnt,
                }
                for a, cnt in action_counts.most_common()
            ]

            return {
                "total_cases": total_count,
                "baseline_precedents": baseline,
                "learned_cases": learned,
                "failure_reasons": reasons_list,
                "outcomes": {
                    "recovered_count": recovered_c,
                    "failed_or_escalated_count": failed_c,
                },
                "actions": actions_list,
            }
        except Exception as e:
            logger.error(f"[ChromaDB:get_playbook_stats] Failed to fetch stats: {e}")
            return {
                "total_cases": total_count,
                "baseline_precedents": 0,
                "learned_cases": 0,
                "failure_reasons": [],
                "outcomes": {"recovered_count": 0, "failed_or_escalated_count": 0},
                "actions": [],
            }

    @classmethod
    def reset_playbook(cls) -> None:
        """Empties the recovery_playbook collection (useful for fresh simulation runs)."""
        client = cls.get_client()
        try:
            client.delete_collection(cls.COLLECTION_NAME)
        except Exception:
            pass
        cls._collection = None
        logger.info("[ChromaDB:reset_playbook] recovery_playbook collection cleared.")
