"""
ID Mapping Module for LiteLLM Provider ID Collision Prevention
Handles OpenAI message ID collisions from non-OpenAI providers
"""

from typing import Dict, Optional

from ..logging_config import get_logger

logger = get_logger(__name__)


class IDMapper:
    """Maps provider IDs to consistent format to prevent collisions"""

    def __init__(self):
        """Initialize ID mapper with empty mapping store"""
        # Mapping: {provider_id -> generated_id}
        self._provider_id_map: Dict[str, int] = {}
        # Reverse mapping: {generated_id -> original_provider_id} (for audit)
        self._audit_map: Dict[int, str] = {}
        # Counter for generating unique IDs
        self._id_counter: int = 0

    def map_provider_id(self, provider_id: str, provider_name: str = "unknown") -> int:
        """
        Map a provider ID to a unique consistent ID

        Handles collisions by:
        1. Checking if provider_id already mapped
        2. If not, generate new unique ID with prefix
        3. Store mapping for audit trail

        Parameters:
            provider_id (str): Original ID from provider (OpenAI, Gemini, etc.)
            provider_name (str): Name of provider for audit trail

        Returns:
            int: Unique consistent ID for this provider_id

        Example:
            provider_id "msg_123" from Gemini → 1001
            provider_id "msg_123" from Claude → 1002 (different provider, different ID)
        """
        if provider_id in self._provider_id_map:
            logger.debug("provider_id_already_mapped", provider_id=provider_id)
            return self._provider_id_map[provider_id]

        # Generate new unique ID (base 1000 + counter)
        self._id_counter += 1
        unique_id = 1000 + self._id_counter

        # Store bidirectional mapping
        self._provider_id_map[provider_id] = unique_id
        self._audit_map[unique_id] = f"{provider_name}_{provider_id}"

        logger.info(
            "provider_id_mapped",
            provider_id=provider_id,
            unique_id=unique_id,
            provider=provider_name,
        )

        return unique_id

    def get_original_id(self, unique_id: int) -> Optional[str]:
        """
        Retrieve original provider ID from audit trail

        Parameters:
            unique_id (int): The generated unique ID

        Returns:
            Optional[str]: Original provider ID with provider prefix, or None if not found
        """
        return self._audit_map.get(unique_id)

    def apply_id_mapping_to_event(self, event: Dict) -> Dict:
        """
        Apply ID mapping to an OpenAI SDK event

        Handles:
        - ThreadItemAddedEvent: Maps item.id
        - ThreadItemUpdatedEvent: Maps item.id
        - ThreadItemDoneEvent: Maps item.id
        - MessageStartEvent: No mapping needed (uses thread_id)

        Parameters:
            event (Dict): Raw event from OpenAI Agents SDK

        Returns:
            Dict: Event with IDs remapped to consistent format
        """
        try:
            event_type = event.get("type", "unknown")

            if event_type in [
                "thread.item.added",
                "thread.item.updated",
                "thread.item.done",
            ]:
                # These events have item.id that may need mapping
                if "item" in event and "id" in event["item"]:
                    original_id = event["item"]["id"]
                    provider_name = event.get("provider", "unknown")

                    # Map the ID
                    mapped_id = self.map_provider_id(original_id, provider_name)

                    # Update event with new ID
                    event["item"]["id"] = mapped_id
                    event["original_id"] = original_id  # Store for audit
                    event["id_remapped"] = True

                    logger.debug(
                        "event_id_remapped",
                        event_type=event_type,
                        original_id=original_id,
                        mapped_id=mapped_id,
                    )

            return event

        except Exception as e:
            logger.error(
                "id_mapping_failed",
                event_type=event.get("type", "unknown"),
                error=str(e),
            )
            # Return event unchanged on error
            return event

    def reset(self):
        """Reset all mappings (for testing or new conversation)"""
        self._provider_id_map.clear()
        self._audit_map.clear()
        self._id_counter = 0
        logger.debug("id_mapper_reset")


# Global instance (stateless per request, so not reused)
_id_mapper_instance: Optional[IDMapper] = None


def get_id_mapper() -> IDMapper:
    """Get or create ID mapper instance"""
    global _id_mapper_instance
    if _id_mapper_instance is None:
        _id_mapper_instance = IDMapper()
    return _id_mapper_instance


def reset_id_mapper():
    """Reset ID mapper for new request"""
    global _id_mapper_instance
    _id_mapper_instance = IDMapper()


__all__ = ["IDMapper", "get_id_mapper", "reset_id_mapper"]
