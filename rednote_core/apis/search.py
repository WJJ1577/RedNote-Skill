"""Search notes API."""

import uuid
from rednote_core.client.session import XHSClient
from rednote_core.apis.models import SearchResult, NoteCard, UserBrief, InteractInfo
from rednote_core.client.exceptions import ParseError


def _generate_search_id() -> str:
    """Generate a search_id in base-36 format."""
    raw = uuid.uuid4().bytes
    n = int.from_bytes(raw[:8], "big")
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []
    while n > 0:
        n, r = divmod(n, 36)
        result.append(alphabet[r])
    return "".join(reversed(result)) if result else "0"


async def search_notes(
    client: XHSClient,
    *,
    keyword: str,
    page: int = 1,
    page_size: int = 20,
    sort: str = "general",
    note_type: int = 0,
) -> SearchResult:
    """Search for notes by keyword."""
    search_id = _generate_search_id()

    payload = {
        "keyword": keyword,
        "page": page + 1,
        "page_size": min(page_size, 20),
        "sort": sort,
        "note_type": note_type,
        "search_id": search_id,
        "image_formats": ["jpg", "webp", "avif"],
        "ext_flags": [],
        "geo": "",
    }

    resp = await client.post(
        "/api/sns/web/v1/search/notes",
        json_data=payload,
    )

    if resp.status_code != 200:
        raise ParseError(f"Search returned {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    if not data.get("success", False):
        raise ParseError(f"Search failed: {data.get('msg', 'unknown')}")

    items = []
    raw_items = data.get("data", {}).get("items", [])
    for item in raw_items:
        nc = item.get("note_card", {})
        if nc:
            items.append(_parse_note_card(nc))

    return SearchResult(
        items=items,
        has_more=data.get("data", {}).get("has_more", False),
        cursor=data.get("data", {}).get("cursor", ""),
    )


def _parse_note_card(nc: dict) -> NoteCard:
    interact = nc.get("interact_info", {})
    user = nc.get("user", {})
    return NoteCard(
        note_id=nc.get("note_id", ""),
        title=nc.get("display_title", ""),
        desc=nc.get("desc", ""),
        type=nc.get("type", "normal"),
        xsec_token=nc.get("xsec_token", ""),
        user=UserBrief(
            user_id=user.get("user_id", ""),
            nickname=user.get("nickname", ""),
            avatar=user.get("avatar", ""),
        ) if user else None,
        interact_info=InteractInfo(
            liked_count=int(interact.get("liked_count", 0)),
            collected_count=int(interact.get("collected_count", 0)),
            comment_count=int(interact.get("comment_count", 0)),
            share_count=int(interact.get("share_count", 0)),
        ) if interact else None,
        tag_list=[t.get("name", "") for t in nc.get("tag_list", [])],
        image_list=[img.get("url", "") for img in nc.get("image_list", [])],
        time=int(nc.get("time", 0)),
        ip_location=nc.get("ip_location", ""),
    )
