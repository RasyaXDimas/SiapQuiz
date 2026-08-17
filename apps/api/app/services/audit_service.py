"""Audit service — mencatat peristiwa penting ke tabel audit_logs.

Dipanggil pada peristiwa auth (user.registered, user.logged_in,
user.logged_out). metadata TIDAK boleh memuat password atau token
(AGENTS.md hard rule #10).
"""

import ipaddress
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.audit_log import AuditLog

logger = get_logger(__name__)

# Key yang nilainya dilarang masuk metadata audit — jaga-jaga redaksi
_FORBIDDEN_META_KEYS = {"password", "token", "refresh_token", "authorization"}


def _valid_ip(value: str | None) -> str | None:
    """Kembalikan nilai hanya bila IP valid; selain itu None.

    Kolom INET menolak nilai non-IP (mis. 'testclient' dari TestClient).
    """
    if value is None:
        return None
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        return None


async def record(
    db: AsyncSession,
    *,
    organization_id: UUID | None,
    actor_user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    safe_meta = {k: v for k, v in (metadata or {}).items() if k not in _FORBIDDEN_META_KEYS}
    log = AuditLog(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        data=safe_meta,
        ip_address=_valid_ip(ip_address),
    )
    db.add(log)
    await db.flush()
    logger.info(
        "audit.recorded",
        action=action,
        entity_type=entity_type,
        organization_id=str(organization_id) if organization_id else None,
        actor_user_id=str(actor_user_id) if actor_user_id else None,
    )
