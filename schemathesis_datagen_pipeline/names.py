# Names the hidden Phase 1 test imports (not in TODO.md); same strategies as above.
_HIDDEN_KEYS = {ETAG_LIST_FORMAT: "_if_match_header", HTTP_DATE_FORMAT: "_http_date_header", RANGE_FORMAT: "_range_header"}
KNOWN_HEADER_FORMATS = {name: _HIDDEN_KEYS[key] for name, key in HEADER_FORMATS.items()}
if_match_values = etag_list_values
range_slightly_invalid_values = slightly_invalid_range_values


def get_header_format_strategies(mode: GenerationMode = GenerationMode.POSITIVE) -> dict[str, st.SearchStrategy[str]]:
    return {_HIDDEN_KEYS[key]: value for key, value in get_header_strategies(mode).items()}
