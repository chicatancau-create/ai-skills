---
name: reference-bilibili-fav-api
description: Bilibili favorite-folder API gotchas — inverted resource/deal params, privacy attr values, FormData delete, lying success_num, and the HTTP 412 write limit.
metadata:
  type: reference
---

User's B站 account: mid `3546602396453260`, uname 周周炜1. Logged into B站 in **Zen** (cookies are
plaintext in `cookies.sqlite`, unlike Chrome/Edge) — see [[reference-zen-browser-data]].

**`POST /x/v3/fav/resource/deal` params are inverted from intuition:**
- `rid` = the **video's aid** (not the folder!)
- `add_media_ids` / `del_media_ids` = comma-joined **favorite folder ids**
- plus `type=2`, `platform=web`, `csrf` (= `bili_jct` cookie)

Passing folder-as-rid returns `code:0, success_num:0` and silently does nothing. **`success_num` lies —
always verify by re-reading `resource/list`.**

Other hard-won facts:
- `resource/list` caps `ps` at **20**; `ps=50` returns `-400 请求错误`.
- Adding to a custom folder does **not** remove the item from 默认收藏夹; issue a second `deal` with
  `del_media_ids` to actually move it.
- `POST /x/v3/fav/folder/add` with `{title, intro, privacy}`: **`privacy=0` → public (attr 22)**,
  **`privacy=1` → private (attr 23)**. Verified anonymously: attr 22 readable, attr 23 → `-403`.
  Omitting `privacy` yields attr 22 = public, so always pass it explicitly.
- `POST /x/v3/fav/folder/del` needs **multipart FormData** with `media_ids` as a **plain id string**
  (not `[id]`, not urlencoded body) plus `platform=web` and `csrf`. Omitting `csrf` gives `-111`,
  sending `media_ids=[id]` gives `-400`.
- `POST /x/v3/fav/folder/edit` takes `{media_id, title, intro, privacy, cover}` urlencoded + csrf.
  On 默认收藏夹 it returned `code:0` and moved attr `0 → 1`, which **is** private (anonymous `-403`) —
  the default folder uses a different attr encoding than custom folders' 22/23.
- `GET /x/v3/fav/folder/info?type=11&fid=...` is unreliable; read attrs from
  `created/list-all?up_mid=<mid>&type=0` instead.
- **After ~40 rapid write POSTs the endpoint starts returning HTTP 412 with an HTML risk-control page**,
  and eventually even GETs fail. It clears in a couple of minutes. Mitigations that worked: keep the
  browser profile across runs (a fresh profile = fresh `buvid3` = "new device"), and pace writes 6–10 s
  apart with 20 s×n backoff.

**Plain `urllib` with the extracted cookies works for reads and for `x/v2/fav/video/add`, but
`resource/deal` no-ops outside a real browser page context.** Drive it from inside a page instead:
launch headless Edge with `--remote-debugging-port` on a throwaway profile, inject the cookies via CDP
`Network.setCookie` (this is what carries httpOnly `SESSDATA`), navigate to a bilibili.com page, then
`Runtime.evaluate` the fetches. Node 24's global `WebSocket` + `fetch` are enough for a ~90-line CDP
client — no npm packages.

Find the real param shapes by fetching the page's own JS bundles and grepping the endpoint path; the
minified caller shows the exact object literal. Cheaper and more reliable than guessing.

Sources for the endpoint list: [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect).
