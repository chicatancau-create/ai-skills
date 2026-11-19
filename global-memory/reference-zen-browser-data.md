---
name: reference-zen-browser-data
description: Where Zen browser stores workspaces / pinned tab groups (sessionstore jsonlz4, not places.sqlite), and how to decode it offline.
metadata:
  type: reference
---

Zen (Firefox fork) profile on this box: `%APPDATA%\Zen\Profiles\0omoaahi.Default (release)` (the other
profile is empty). `installs.ini` / `profiles.ini` confirm which one is live.

**Tab groups and workspaces are NOT bookmarks.** They live in
`sessionstore-backups/recovery.jsonlz4` (rewritten every ~15 s while running), not `places.sqlite`.
If a user shows you a sidebar of categorized tabs that has no match in the bookmark tree, look here.

- `windows[0].groups` / `.folders` → tab-group name, `id`, `workspaceId`, `prevSiblingInfo` ordering chain.
- `windows[0].spaces` → workspaces (uuid + name).
- `windows[0].tabs[]` → `zenWorkspace` (uuid) says which workspace; group membership is positional:
  each group is anchored by an `about:blank` placeholder tab (its id appears in that folder's
  `emptyTabIds`), and the tabs following it until the next placeholder belong to that group.
  `extdata.groupId` / `extdata.parentId` are **not** populated, so don't hunt for them.

**Decoding:** header is `mozLz40\x00` (8 bytes) + uint32 LE uncompressed length + a plain LZ4 *block*
(not LZ4 frame). A ~35-line pure-stdlib Python LZ4 block decoder handles it; expand back-references by
doubling a `tail` slice rather than copying byte-by-byte. `bookmarkbackups/*.jsonlz4` use the same framing.

`places.sqlite` is safe to read by copying `.sqlite` + `-wal` + `-shm` next to each other and opening with
`file:...?mode=ro`. Bookmarks-only dedupe must join `moz_bookmarks.type=1` to `moz_places` —
`moz_places` alone is the whole browsing history and will over-match.

See also [[reference-bilibili-fav-api]], [[reference-inapp-browser-verification]].
