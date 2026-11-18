# YTP Agents transcripts

Source playlist: https://www.youtube.com/playlist?list=PLDdUVGwLJW7I
Private playlist by Tung Ho, 11 videos. Videos 01-03 fetched 2026-10-30, videos 04-11 fetched 2026-11-18.

Method: yt-dlp (`--write-auto-subs --sub-langs en --sub-format srt`) for videos 02, 04, 05, 06, 08, 09.
Videos 01, 03, 07, 10 and 11 hit YouTube HTTP 429 rate limits on subtitle downloads, so those came via youtube-transcript-api instead.
All captions are English auto-generated. Transcript-API SRT files were assembled from its cue data (timestamps and wrapped lines).
Plain-text files are the deduplicated cue text joined into one paragraph, so rolling-caption repeats are removed.

## Videos

01 - EvaDsV_HHSU - 30 minutes learning, 65 plus Claude agents, one Chief Agent, coordinated PMs, self-improving loops - about 27 min - 5445 words - https://www.youtube.com/watch?v=EvaDsV_HHSU
02 - SgBKD8wm89k - Agentic Coding at Scale, Verification Loops That Actually Work, Anthropic - about 56 min - 8641 words - https://www.youtube.com/watch?v=SgBKD8wm89k
03 - O8cl4R5VEOI - How I Am Actually Using AI These Days - about 25 min - 5838 words - https://www.youtube.com/watch?v=O8cl4R5VEOI
04 - JQKjxmMZJj4 - Stop Auditing Excel Manually, Let Claude Do It - about 26 min - 4519 words - https://www.youtube.com/watch?v=JQKjxmMZJj4
05 - 8fvUXkotDPc - Building Apps with AI Is Hard Until You Learn This - about 31 min - 6129 words - https://www.youtube.com/watch?v=8fvUXkotDPc
06 - TFCDWrEBaFM - How Claude Fixes Its Own Code - about 42 min - 9306 words - https://www.youtube.com/watch?v=TFCDWrEBaFM
07 - qwY_OAoHt7s - The 90/10 plan that AI Proofs your Career - about 11 min - 2629 words - https://www.youtube.com/watch?v=qwY_OAoHt7s
08 - vlfCjWuv4es - Rethinking Claude Code Best Practices, Lydia Hallie, Anthropic - about 18 min - 3328 words - https://www.youtube.com/watch?v=vlfCjWuv4es
09 - qfZhblrmSxM - I hate that Theo was right - about 19 min - 3586 words - https://www.youtube.com/watch?v=qfZhblrmSxM
10 - V5X34C9qvX4 - The Right Way to Use AI for Writing, Presentations, and Engineering Docs - about 51 min - 10360 words - https://www.youtube.com/watch?v=V5X34C9qvX4
11 - ZBTegd8DUZM - LIVE: Writing code that doesn't suck with the creators of Pi - about 46 min - 8884 words - https://www.youtube.com/watch?v=ZBTegd8DUZM

## Files

Each video has `NN-videoId.en.srt` (timestamped cues) and `NN-videoId.en.txt` (plain text, one paragraph).

02 `-Agentic Coding at Scale...` SRT and 02 info JSON keep their original yt-dlp filenames.
00 playlist info JSON (video count, modified date) from yt-dlp is included for metadata, refreshed 2026-11-18.

Videos 07, 10 and 11 were still returning HTTP 429 from yt-dlp's subtitle endpoint at fetch time. Re-run the yt-dlp command for those IDs later to replace the transcript-API SRTs with native yt-dlp files; the caption text itself is the same auto-generated track.
