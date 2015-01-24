# Grep for a field, then knock out another.
["-k", ".features > *:has(:contains(\"Aruba\"))", "-v", ".coordinates", "tests/data/basic.geo.json"]
