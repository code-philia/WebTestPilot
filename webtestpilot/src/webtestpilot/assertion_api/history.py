from webtestpilot.baml_client.types import History
from webtestpilot.data_models import Session


def serialize_history(session: Session) -> list[History]:
    """
    Serialize session history for prompt consumption.
    Each logical page contributes layout/description only once.
    """
    seen_pages: set[str] = set()
    history: list[History] = []

    for state in session.history:
        page = state.page
        first_seen = page.page_id not in seen_pages

        history.append(
            History(
                page_id=page.page_id,
                layout=page.layout.toprettyxml(indent="  ") if first_seen else None,
                description=page.description if first_seen else None,
                prev_action=state.prev_action,
            )
        )

        seen_pages.add(page.page_id)

    return history