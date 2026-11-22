# 规则：工作区不留视频，交付即清中间产物

- 来源：用户 2026-11-22（m01552）：「成品视频已经 OK 了，不需要再留在工作区，可以把它删掉。工作区的视频还是尽量不要留着。」＋「把产生的垃圾给我清除掉」（m01560 补充：因为要归档本会话）。
- 规则：`G:\AIrenwu` 工作区**不存视频/音频大中间产物**。成品导出落 `D:\AI-Tool-State\<任务>\输出\`；渲染/混音缓存落 `D:\AI-Tool-State\<任务>\*-cache\`；工作区证据只留小体积图/文（jpg/png/srt/json/ass/md）。交付经用户确认后删成品与缓存。
- 已落地（2026-11-22）：`export_final.py` 的 OUT/MEDIA、`review_render.py` 的 MEDIA 改指 D 盘（工作区 REV 只写 jpg/ass/srt）；本轮清除 37 文件+3 目录 ≈2.0GB（工作区 seg*/fin_seg*/final_video/review_full/mix wav/成品 mp4；D 盘 vibeclip 仓库+zip、不完整 vosk zip、 superseded 草稿备份 v2/v3、被取代的 16k/电话音质 wav）。
- **例外（删了会坏）**：CapCut 草稿引用的源媒体必须保留在 D 盘——`素材\origins\`（7 原片备份）、`素材\graded\105134_graded.mp4`、`bgm_calm.mp3`、`narr_orig.m4a`；删它们=草稿丢媒体。模型权重另见 rule-models-store-in-d-models.md。
- 操作提示：删前 Get-ChildItem/glob 核对清单与体积；同卷删除瞬时；删后 grep/glob 复核工作区媒体残留=0。
- 关联：手册 `03-通用/04-工程规范与安全/规则-工作区不留视频-交付即清中间产物.md`；[[规则-任务区与手册一体化联动]]。