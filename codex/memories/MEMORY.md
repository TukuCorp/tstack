# Task Group: csim-copy QA feedback-round final polish (N1-N4) and QA-loop docs
scope: Close QA feedback rounds in the CarbonSim clone (chart legend overlap, language contrast, setup form ids/percentages, QA-loop docs) with red/green TDD, browser-measured verification, full gate green, no commits, and :5003 serving kept up.
applies_to: cwd=C:\Users\tukum\Downloads\csim-copy; reuse_rule=checkout-specific (net9.0 Blazor InteractiveServer on main f7943b9, 84 changed files uncommitted); the red/green plus no-commit plus :5003-serve plus herdr-report discipline is reusable wherever the same QA-loop rules are stated

## Task 1: N3 setup form ids, labels, and shares-as-percentages

### rollout_summary_files

- rollout_summaries/2026-10-10T10-21-45-ghKX-qa_round7_final_polish_n1_n4.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\10\rollout-2026-10-10T17-21-46-01a12555-3e2a-72d2-87e0-97e08b635403.jsonl, updated_at=2026-10-10T16:22:06+00:00, thread_id=01a12555-3e2a-72d2-87e0-97e08b635403, QA round 7 N1-N4 closed, full gate green, :5003 serving)

### keywords

- N3-setup-percent, AdminSetup.razor, Percent, SetPercent, SetupPercentHint, setup-sector, setup-abatement, setup-growth, sr-only, definition-list, AdminScreensTests, resx-parity

## Task 2: N1 chart legend overlap plus N2 language contrast, browser-verified

### rollout_summary_files

- rollout_summaries/2026-10-10T10-21-45-ghKX-qa_round7_final_polish_n1_n4.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\10\rollout-2026-10-10T17-21-46-01a12555-3e2a-72d2-87e0-97e08b635403.jsonl, updated_at=2026-10-10T16:22:06+00:00, thread_id=01a12555-3e2a-72d2-87e0-97e08b635403, QA round 7 N1-N4 closed, full gate green, :5003 serving)

### keywords

- N1-legend-overlap, N2-language-contrast, ECharts-SVG, charts.js, grid.top, legend-scroll, nav-ink, WCAG-contrast, PlaywrightFeedbackTests, Contrast, LegendOverlaps

## Task 3: N4 QA-loop docs plus serve plus herdr report

### rollout_summary_files

- rollout_summaries/2026-10-10T10-21-45-ghKX-qa_round7_final_polish_n1_n4.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\10\rollout-2026-10-10T17-21-46-01a12555-3e2a-72d2-87e0-97e08b635403.jsonl, updated_at=2026-10-10T16:22:06+00:00, thread_id=01a12555-3e2a-72d2-87e0-97e08b635403, QA round 7 N1-N4 closed, full gate green, :5003 serving)

### keywords

- N4-docs, activeContext, QA-loop-index, lessons, trainer-runbook, Change-rules, :5003, herdr-report, w2C:p2, fidelity-run, calibration-grid

## User preferences

- when fixing UI, the user said "Red/green where code changes, no commits, keep :5003 serving" -> run the failing test first, never commit, restart the host serving on :5003 after the change [Task 1]
- when N3 asked, the user said show percentages as percentages (accept 3 or 3%), store fractions internally with hint under each field -> default to percent display with dual-parse plus a hint under each field [Task 1]
- when N2 still looked blue, the user said "verify in a browser, not the stylesheet, a more specific rule may be overriding" -> measure computed style in Playwright, not CSS reading [Task 2]
- when N1 overlapped on phones, the user expected reserve space so the legend sits above the plot when wrapped -> increase grid.top plus scroll legend [Task 2]
- when N4 asked, the user said activeContext QA loop index, lessons 2 items, trainer-runbook price-path plus Change-rules -> update all three docs [Task 3]
- when done, the user said "Report back with: herdr agent prompt w2C:p2 "<short report incl. final test counts>" and do not wait for a reply" -> send the single-line herdr prompt to w2C:p2, do not wait [Task 3]

## Reusable knowledge

- AdminSetup.razor percent pattern: display via Percent(decimal?) as "3%", parse via SetPercent accepting "3" or "3%" dividing by 100; shares stay fractions in DraftParameters. [Task 1]
- Every setup input needs id plus label for=id; repeated abatement/growth rows use for-loop index ids (setup-sector-{s}-*, setup-abatement-{s}-{o}-*, setup-growth-{g}-*) with sr-only labels; add .sr-only CSS. [Task 1]
- SetupPercentHint resx key must exist in both en and vi or LocalizationTests fails key-parity; hint inside dl.metrics must live in dd (span.hint), not p inside dl, or axe definition-list fails. [Task 1]
- Charts render to canvas by default; switch wwwroot/js/charts.js echarts.init(element,{renderer:"svg"}) to make legend/axis text measurable and crisper. [Task 2]
- Prices grid.top 34->60 with legend type:"scroll"; Macc grid.top 24->44; unit test locks top>=52/44 and legend type scroll. [Task 2]
- N2 root cause: .lang a had no rule, fell through to a{color:var(--blue)}; fix .topbar .lang a:link/visited color:var(--nav-ink) plus focus-visible outline; browser test computes WCAG contrast >=4.5 and no underline. [Task 2]
- Playwright legend probe must filter by option.legend names and compare against yAxis name plus top tick; naive all-text overlap false-positives on scroll counter "1/2". [Task 2]
- activeContext.md already has Review round 1-6; append Review round 7 plus Review QA loop index with fixed/accepted-limits table. lessons.md lesson 6 = sweep every lever before claiming mutually exclusive; cross-ref seeding rule in lesson 2. trainer-runbook.md S4 Change-rules card plus S8 measured envelopes (100.00/181.84/255.97, 9.0% discount, 1.00% abatement). [Task 3]
- Keep :5003 serving via dotnet run --project src/CarbonSim.Web --no-build -- --urls http://localhost:5003 --environment Development; Start-Process blocked by policy, direct exec_command works; stale CarbonSim.Web locks build output -> Stop-Process before build/test. [Task 3]
- Final gate shape: build 0W/0E; Engine 259+2 skip, Data 16, Web 179+1 skip; format only pre-existing CHARSET on GovernmentReserveToAuction migration. [Task 3]

## Failures and how to do differently

- First cut placed <p> hint inside dl.metrics div -> axe definition-list serious violation; moved hint to span inside dd and re-ran PlaywrightAccessibilityTests green. [Task 1]
- Added Percent/SetPercent markup before helpers existed -> 15x CS0103 red; added helpers then green - expected red/green sequence. [Task 1]
- First legend probe compared every text pair -> tripped on "Offset" vs "1/2" counter; tightened to title plus plot-top check. [Task 2]
- Non-vacuous check: restoring grid.top 34 fails with "legend Vintage 1 lands on axis title", 60 passes; keep the revert-check when claiming overlap fixed. [Task 2]
- Full-suite Playwright run surfaced 2 admin failures then isolated to axe dl violation; fixed markup not test. [Task 3]
- exec_command long tests yield to background session; must poll via write_stdin/wait with session_id. [Task 3]

# Task Group: csim-copy-calib bot calibration and reserve re-offer (bot-calibration worktree)
scope: Calibrate CarbonSim clone rule-based bots toward the four open fidelity envelopes and build a reserve-to-auction re-offer mechanism, isolated in the csim-copy-calib worktree while another agent works in csim-copy.
applies_to: cwd=C:\Users\tukum\Downloads\csim-copy-calib; reuse_rule=worktree-specific (branch bot-calibration off main 8a44a34); never copy wording from carbonsim.org or research/; the herdr calib-report format is reusable wherever HERDR_ENV=1

## Task 1: Bot calibration worktree setup, aborted before tuning

### rollout_summary_files

- rollout_summaries/2026-10-04T12-36-10-37Bz-carbonsim_bot_calibration_worktree_setup.md (cwd=C:\Users\tukum\.codex\app-server-daemon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T19-36-10-01a106ea-2583-7933-8792-b4b7abc9cf4d.jsonl, updated_at=2026-10-04T12:38:59+00:00, thread_id=01a106ea-2583-7933-8792-b4b7abc9cf4d, worktree created, no tuning before abort; work happens in C:\Users\tukum\Downloads\csim-copy-calib)

### keywords

- bot-calibration, git worktree add, FidelityTests, FidelityRun, ComplianceBot, BotSettings, seeded run, vietnam-2024.json

## Task 2: Bot calibration plus reserve-to-auction re-offer, partial

### rollout_summary_files

- rollout_summaries/2026-10-04T12-39-38-k34p-carbonsim_bot_calibration_reserve_reoffer.md (cwd=C:\Users\tukum\.codex\app-server-daemon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T19-39-38-01a106ed-51da-73d3-8bbf-a153a6be8d4d.jsonl, updated_at=2026-10-04T15:25:09+00:00, thread_id=01a106ed-51da-73d3-8bbf-a153a6be8d4d, price-path envelope closed; full compliance structurally blocked without banking; 403 passed 4 skipped 0 failed; uncommitted)

### keywords

- ComplianceBot bid spread, WillingnessToPay, GovernmentReserveToAuctionPercent, AuctionSchedule.ReofferReserve, AddLot top-up, vintage premium, offset share, discount haircut, herdr agent prompt

## User preferences

- when calibrating in a shared repo, the user said use git worktree add plus -b bot-calibration and do all work and builds there with Do NOT work in the original folder -> verify worktree and branch before any build or test [Task 1]
- when working fidelity envelopes, the user required red/green TDD by un-skipping or writing the failing envelope test first and watching it fail, then tuning, with deterministic seeded randomness; never weaken an envelope and never copy from carbonsim.org or research verbatim [Task 1][Task 2]
- when finishing, the user required zero build warnings plus the whole dotnet suite green, an activeContext.md review update, no commit and no push, and a stop after two failed fixes on the same failure [Task 1][Task 2]
- when done or blocked, the user required one herdr agent prompt csim-copy calib report as a single line under 1500 chars with no double quotes covering envelopes plus measured vs targets, files changed, test results, and open items [Task 1][Task 2]

## Reusable knowledge

- Baseline before tuning: 7 pass 4 skipped; compliance 346 company-years short with 19.8Mt uncovered at Normal, price path 100.00/101.60/106.77, offset share 6.09 percent vs 2-3 percent envelope, shock 0 percent with no mechanism; BotSettings Normal/Hard/Easy values are placeholders. [Task 1]
- ComplianceBot fix that closed price-path: bid the whole position spread over sectionsLeft at WillingnessToPay by walking remaining abatement cheapest-first capped at PenaltyPerTonne, re-Abate at the Trade trigger, amortise capital over operatingYearsLeft, floor bid volumes to whole tonnes, split across usable lots with vintage<=year; shipped Normal reached 100.00/108.62/220.51 with discount 20.8 percent. [Task 2]
- Reserve-to-auction mechanism: AuctionSchedule.ReofferReserve runs at year-last-close oldest-vintage-first with an AddLot top-up on the same-vintage lot; GovernmentReserveToAuctionPercent defaults 0 for exact-today behaviour with persistence plus migration plus admin setup and EN/VI resx; annual re-offer is envelope-safer than per-auction cascade which over-supplies every auction to the floor. [Task 2]
- Structural finding: 34-40Mt uncovered because Government.Return retires unsold volume that is never re-offered; every compliance-helping lever broke price/vintage/leaderboard, so full compliance plus price path needs fleet banking. [Task 2]
- Discount definition: (allowAvg-offsetAvg)/allowAvg volume-weighted; bots quote a fixed 15 percent/5 percent haircut to the last auction, so 15-17 percent variants are mix effects. [Task 2]

## Failures and how to do differently

- Cheapest-MAC cap held prices at the floor; lifetime-cost ranking built 12-15y projects for 1-2y left pushing the leaderboard to 157/t; banking-tranche and forward-lot buying softened the tight year and broke the vintage premium; 1.5x bid buffer narrowed the discount margin without helping compliance. [Task 2]
- PowerShell-via-exec quoting is fragile for Get-Content plus Substring patterns and PowerShell edits can corrupt file encoding; use plain Get-Content -LiteralPath -Raw and re-apply patches after checkout when corruption appears. [Task 1][Task 2]
- A flaky Playwright admin test passed on rerun without a product change; treat single rerun passes as noise, not proof. [Task 2]

# Task Group: csim-copy CarbonSim admin console, Vietnam localisation, and hardening (Phase 4-6)
scope: Implement Phase 4 Blazor admin console (run controls, reports, multi-run isolation), Phase 5 Vietnam localisation (vi resx, vi-VN number entry, VND display, scenario cross-check, trainer runbook), and Phase 6 hardening (load test, Docker/Postgres/backup, a11y/phone pass, handover) in the CarbonSim clone with RED/GREEN TDD gates and herdr reporting.
applies_to: cwd=C:\Users\tukum\Downloads\csim-copy; reuse_rule=checkout-specific (net9.0 Blazor InteractiveServer); do not commit unless asked; never copy wording from carbonsim.org or the research catalog

## Task 1: Phase 4 admin console end-to-end, success

### rollout_summary_files

- rollout_summaries/2026-10-03T10-56-49-fTxV-phase4_admin_console_csim_copy.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\03\rollout-2026-10-03T17-56-51-01a10168-d46b-7483-927b-6552c745ccbb.jsonl, updated_at=2026-10-03T11:37:45+00:00, thread_id=01a10168-d46b-7483-927b-6552c745ccbb, gates green: build 0W/0E, full sln 360, Playwright 3 passed; uncommitted)

### keywords

- Phase4, admin console, Blazor InteractiveServer, SimulationRegistry, SimulationClockService, AdminSession, AllocationPlan.ApplyEmissionShock, RegistrationPolicy, AdminCsv, ScenarioDraft, RunIsolation, PlaywrightAdminTests

## Task 2: Phase 5 Vietnam localisation and scenario, success

### rollout_summary_files

- rollout_summaries/2026-10-03T12-12-48-EXyd-phase5_vietnam_localisation_csim_copy.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\03\rollout-2026-10-03T19-12-49-01a101ae-6417-7da1-a815-792e177b2695.jsonl, updated_at=2026-10-03T12:44:03+00:00, thread_id=01a101ae-6417-7da1-a815-792e177b2695, 376 pass/4 skip gate green; uncommitted)

### keywords

- Phase5, vietnam-localisation, SharedStrings.vi.resx, CurrencyDisplay, Display.Currency, bind-culture, NumberEntryTests, PlaywrightVietnamTests, fidelity-envelopes, trainer-runbook, TradingOpenShareOfYear

## Task 3: Phase 6 hardening and deployment, success

### rollout_summary_files

- rollout_summaries/2026-10-03T19-14-30-vRxL-phase6_hardening_deployment_csim_copy.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T02-14-30-01a10330-767d-7e63-a5c7-ab850f6cd919.jsonl, updated_at=2026-10-03T20:09:03+00:00, thread_id=01a10330-767d-7e63-a5c7-ab850f6cd919, 392 passed/5 skipped with Playwright real; load full run once; uncommitted; single herdr PHASE6 REPORT sent)

### keywords

- Phase6, load test 250 clients, SharedViewCache, LoadHarness, Docker, Postgres provider, VACUUM INTO backup, axe-core, PlaywrightAccessibilityTests, handover, herdr agent prompt

## Task 4: Verify, commit, and push Phase 6 hardening on main, success

### rollout_summary_files

- rollout_summaries/2026-10-04T04-19-16-uMpM-git_commit_push_main_phase6_hardening.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T11-19-16-01a10523-369e-7150-a5c3-bdfb248c2a9e.jsonl, updated_at=2026-10-04T04:26:51+00:00, thread_id=01a10523-369e-7150-a5c3-bdfb248c2a9e, 44 files +2214/-131 as 8a44a34; tree clean and in sync with origin/main)

### keywords

- git commit push, origin/main, 8a44a34, dotnet build, dotnet test, Engine 238, Data 16, Web 138, session wait, NativeCommandError

## Task 5: Fix two flaky-test root causes and prove 10 consecutive green Web runs, success

### rollout_summary_files

- rollout_summaries/2026-10-04T12-39-44-4X6M-csim_copy_flaky_web_tests_fix.md (cwd=C:\Users\tukum\.codex\app-server-daemon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T19-39-44-01a106ed-66bb-7c02-aa18-a6e1bc8c60d0.jsonl, updated_at=2026-10-04T14:08:40+00:00, thread_id=01a106ed-66bb-7c02-aa18-a6e1bc8c60d0, 10x trx all Completed 138 passed 0 failed; full sln Engine 238+4skipped Data 16 Web 138+1skipped; uncommitted; herdr report sent)
- rollout_summaries/2026-10-04T12-36-14-iTHV-flaky_web_test_triage_aborted.md (cwd=C:\Users\tukum\.codex\app-server-daemon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\04\rollout-2026-10-04T19-36-14-01a106ea-331d-7563-a340-7ec145d8c6df.jsonl, updated_at=2026-10-04T12:39:35+00:00, thread_id=01a106ea-331d-7563-a340-7ec145d8c6df, aborted before reproduction; predecessor triage only)

### keywords

- flaky Web tests, Playwright prerender click loss, RendererInfo.IsInteractive, InteractivePage.WaitUntilInteractiveAsync, SQLite ClearAllPools vs ClearPool, trx logger, herdr agent prompt

## User preferences

- when the brief states a legal rule, the agent reworded 4 SharedStrings.resx values in its own words and added no new verbatim catalog sentences -> treat the research catalog as naming authority only and never ship its wording [Task 1]
- when working from harvested research, the legal rule is: never copy code/CSS/JS/strings/assets from carbonsim.org; the Vietnamese glossary is terminology authority only, write sentences yourself, and scenario notes must state derived vs invented -> author all copy and annotate notes [Task 2]
- when the brief says work autonomously, the user expects no check-ins until the single final report -> batch all Phase work then report once in the mandated herdr agent prompt format, and when a brief offers a test-project vs tools choice, record why the choice was made [Task 3]
- when asked to "git commit push main" with no message supplied -> verify build plus tests first, then commit with a generated scope-summary message and push [Task 4]
- when fixing a flaky test, the user asked to "Fix it properly: no retries, no longer sleeps, no skips. If the root cause is a product bug, fix the product and add a deterministic test that proves it. Then show 10 consecutive clean runs" -> fix the product/harness deterministically with trx proof, never timing workarounds; a HubException naming Delta/Red River Power is expected refusal noise asserted by HubAuthorizationTests, not the flake [Task 5]

## Reusable knowledge

- Engine pattern: AllocationPlan.ApplyEmissionShock(unit,year,delta) writes into the BAU path, clamps at 0, refuses 0-delta, survives snapshot; validated by EmissionShockTests (4 tests). [Task 1]
- Admin mutation pattern: AdminSession -> SimulationClockService takes the run Gate, mutates, CollectAnnouncement under gate, broadcasts after release to per-simulation SignalR group (same path as tick); run identity is seed-derived and CreateRun refuses duplicates. [Task 1]
- Admin auth: Blazor pages under /admin sit behind AdministratorPolicy and AdminSession re-checks role every call; AdminSession must prefer HttpContext.User when present, else AuthenticationStateProvider wrapped in try/catch InvalidOperationException outside the circuit. [Task 1]
- Setup edits stay pending via ScenarioDraft (JSON mirror of ScenarioFile) -> ToJson -> ScenarioLoader.LoadJson -> runs.Start Pending + Save; live parameters render read-only. Player messaging-off: PostMessageAsync throws, PlayerView disables the form and shows MessagingSwitchedOff. [Task 1]
- Currency approach: engine stays single internal unit (USD, what the trainer deck quotes); UI-only conversion via CurrencyDisplay.cs (Code, VndPerUsd, ToDisplay/ToInternal, Money/Money2 appends code); host options DisplayCurrency+VndPerUsd validated in Program.cs; CSV stays internal invariant. [Task 2]
- Number entry under vi-VN (comma decimal, dot grouping): replace type=number with type=text inputmode=decimal plus @bind:culture=CultureInfo.CurrentCulture on numeric inputs only; Blazor has no @bind:format for numerics (DateTime-only, causes CS1503/CS0029) so drop format; range sliders stay InvariantCulture. [Task 2]
- Localisation plumbing: culture cookie carbonsim.culture already reaches the Blazor circuit, no extra plumbing needed; add SharedStrings.vi.resx plus new keys to both resx; cap displays must use Display.Tonnes not Display.Money. [Task 2]
- Test patterns: LocalizationTests reads both .resx off disk for key parity plus real localiser via AddLogging+AddLocalization under vi-VN; CultureScope saves/restores cultures; StubPlayerSession records invariant strings via FormattableString.Invariant; NumberEntryTests must look up button labels via Localizer[Key] not English literals; PlaywrightVietnamTests switches via /culture/set then asserts translated headings and grouping. [Task 2]
- Vietnam scenario cross-check: deck EN via pdftotext (ETS parameters slide p19: 355,850,000, 3%/yr, 90%, 4/yr, 100/300, 10%, 300+1); existing vietnam-2024.json already matched, kept file and rewrote notes with cross-check; FidelityTests 7 pass/4 skip with recorded Normal/Hard values. [Task 2]
- Load-test pattern: revision-keyed Shared cache invalidated in CollectAnnouncement carries run-wide work once per change with per-player slices only; 250-client uncompressed 20-min year measured 4 auctions missed 0 maxLateness 895ms, refresh p50 3.67ms p95 9.72ms p99 15.15ms, gate p50 0.01ms, actions 1608 refused 3984 errors 0, peakWS 164MB; spike is the once-per-year save holding the gate. Full run is opt-in via CARBONSIM_LOAD_FULL=1 with a compressed Smoke in the normal suite. [Task 3]
- Deployment facts: Postgres builds from the model (FromModel), not SQLite migrations, with unknown-provider and Postgres+Migrate refused at startup; SQLite backup must be VACUUM INTO into a copy, never a file copy; Docker files were written without claiming a build since docker is absent; backup drill proven by SqliteBackupRestoreTests (seeded year, save, VACUUM INTO, reopen copy, reload, leaderboard/clock match). [Task 3]
- Accessibility pass: palette fixed to 4.5:1 or better (--muted #646b78 4.95:1, --blue #2f6fbf 5.06:1), :focus-visible ring, tabindex on card-wide, aria-labels on setup/table inputs, fixed div.metrics dlitem, role=img charts, role=log messages; vendored axe-core 4.10.2 runs wcag2a/wcag2aa/wcag21a/wcag21aa over 11 player plus 5 admin screens with 0 violations plus an admin 390x844 overflow pass. [Task 3]
- Handover record: docs/handover.md holds the arch map, mechanic table, and open gaps (4 fidelity envelopes, bot calibration, in-mem queues, single currency, inert tradingOpenShare, per-refresh account lookup, Postgres/Docker unverified); gates were build 0W/0E, test 392 passed 5 skipped with Playwright real, format clean, host DLL serving /sign-in /admin / at 200; exactly one herdr agent prompt csim-copy PHASE6 REPORT then stop, no commit. [Task 3]
- Pre-push gate in this repo: dotnet build CarbonSim.sln with minimal verbosity must show 0 warnings 0 errors, then dotnet test suites green (baselines at push: Engine 238 passed plus 4 skipped, Data 16 passed, Web 138 passed plus 1 skipped); commit 8a44a34 covered 44 files +2214/-131 with message "Phase 6 hardening: Docker deployment, Postgres provider switch, SQLite backup/restore, load harness, accessibility tests, player/admin UI polish". [Task 4]
- Blazor prerender click/change-loss pattern: gate Playwright tests on interactive render via a data-interactive marker set only when RendererInfo.IsInteractive plus WaitUntilInteractiveAsync after every navigation; a connected WebSocket is not a sufficient readiness gate. Vietnam OTC volume default 1_000 vs typed 1.500 signals a lost @bind change event; admin create-run no-navigation with connected socket signals a pre-hydration click. [Task 5]
- SQLite ClearAllPools is process-wide and breaks parallel xUnit hosts sharing one process; per-host teardown must ClearPool only its own Data Source. Data.Tests ClearAllPools is safe only because it runs in a separate process. Post-fix baselines: build 0W/0E, Engine 238+4 skipped, Data 16, Web 138+1 skipped. [Task 5]

## Failures and how to do differently

- Razor Strings[key] inside @onclick lambdas fails CS1003/CS1501 -> extract to named methods and avoid inline indexer in lambdas. [Task 1]
- AdminSession calling GetAuthenticationStateAsync from an HTTP endpoint throws InvalidOperationException -> check IHttpContextAccessor first, wrap provider call in try/catch. [Task 1]
- PlayerScreensTests asserting verbatim catalog wording broke after reword -> assert via Localizer(Services)[key].Value instead. [Task 1]
- dotnet format --verify-no-changes import-order errors mean System.* first (dotnet_sort_system_directives_first=true); a prior dotnet format run may have fixed files silently, so verify again. dotnet test projA projB fails MSB1008 -> test projects one at a time or the whole sln. [Task 1]
- Building vi.resx via apply_patch with inline content failed verification -> store the en resx and build vi via a string-replace map script instead of a huge patch. [Task 2]
- First @bind:culture attempt with @bind:format=N0/N2 broke the build (numeric format unsupported) -> drop @bind:format entirely. An over-broad script added @bind:culture to text/string fields -> revert to numeric-only conversions. [Task 2]
- dotnet format/test output redirection to file held locks -> use file plus Add-Content pattern with waits; gate-check scripts with non-ASCII literals cause parser errors -> use lang= regex not literal Vietnamese text. [Task 2]
- Phase completion signal is a single herdr agent prompt csim-copy with PHASE REPORT then stop; did not commit/push, did not touch AGENTS.md. [Task 1][Task 2]
- Load-harness setup traps: give the session a RunId plus an Acting flag (undefined runId/acting bugs otherwise); force StartDemoSimulation=false or seeding reports seed already under way; a compressed clock needs a pacing delay or the refresh count reads too low. [Task 3]
- Compose/deployment patches break on ${} and backticks -> escape \${ or build the file from a line array; axe patch breaks on string.Join("; ") -> use concatenation; activeContext patch fails on em-dash -> use PowerShell Replace. [Task 3]
- Long tests need file redirect plus session polling, and inline Start-Process is blocked -> start the session dll and probe separately; clean fullload.log/gate-test.log and kill leftover chrome before finishing. [Task 3]
- Long dotnet test runs return EXIT:undefined with only "A total of 1 test files matched" on the first poll -> use the session wait pattern with 180-240s yields, not a retry; about 5 skips are normal here. [Task 4]
- git push origin main prints NativeCommandError/RemoteException text with EXIT:1 even on success ("deb6e4c..8a44a34 main -> main") -> confirm with git status --short --branch plus git log --oneline -2 showing a clean tree in sync with origin/main. [Task 4]
- Reproduce flakes with bounded discrete trx-logged runs (12x loop), not a held-open session: write_stdin polling on a long dotnet test session repeatedly returns empty and stalls progress. Light-load probe passes can mask a load-sensitive race, so capture under parallel load with run-count plus recovery-click evidence. [Task 5]
- bUnit Renderer access seals the service collection: SetRendererInfo must come last in the fixture ctor after service registrations or 56 tests fail with cannot-register-services; on .NET9 the working signature is new RendererInfo("Server", true). [Task 5]
- apply_patch with relative paths writes into the daemon cwd, not the repo: use absolute C:/Users/tukum/Downloads/csim-copy/... paths and verify file existence after each patch. [Task 5]

# Task Group: csim-copy CarbonSim replication research and engine build (Phases 0-1)
scope: Assess what is replicable for an EDF CarbonSim clone from local reports plus web sources, then orchestrate a herdr omp builder through engine Phases 0-1 with batched prompts plus independent verification.
applies_to: cwd=C:\Users\tukum\Downloads\csim-copy; reuse_rule=checkout-specific (research is spec, never ships; firm names must be invented); herdr orchestration pattern is reusable wherever HERDR_ENV=1

## Task 1: Replication assessment plus web harvest, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-pdOz-carbonsim_replication_research_engine_build.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b546-7142-b326-4ed32aa23cab.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b546-7142-b326-4ed32aa23cab, functional clone near 80 percent; rules 85, screens 70, admin 60, numeric 30)

### keywords

- carbonsim replication assessment, EDF spec, sim3.carbonsim.org, resourcestrings 883 keys, vncarbonmarket Wayback, ETP deliverables, confidence split

## Task 2: Engine Phases 0-1 via herdr omp builder, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-pdOz-carbonsim_replication_research_engine_build.md (cwd=C:\Users\tukum\Downloads\csim-copy, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b546-7142-b326-4ed32aa23cab.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b546-7142-b326-4ed32aa23cab, 232 passed 4 skipped; committed e85c910 and pushed; Phase 2 batch blocked on builder credit limit)

### keywords

- herdr omp builder, deepseek-v4.1-flash, batched prompts, independent verification, Auction clearing, invented firm names, fidelity envelopes

## User preferences

- when asked to assess replication, the user said: "What info do I have ready, what is available further on web and what am I missing still? Right now what is degree of confidence in full replication" -> answer as a ready / web-available / missing split with quantified per-layer confidence, saved as a brief [Task 1]
- when asked for YouTube insights, the user wants transcripts plus a screen inventory usable as an acceptance script without rewatching [Task 1]
- when asked whether ETP/UNOPS deliverables exist anywhere, the user wants proof-of-absence via enumeration (2725-item media scan, Wayback uploads, VI/EN plus gov/unops/ICAP routes), not just a search summary [Task 1]
- when the user said "use herdr skill launch omp agent with deepseek flash v4.1 model in new tab same space" and "babysit agent in omp-builder herdr tab to complete phase 2 same cadence" -> orchestrate in a new tab with that model using batched prompts plus independent verification plus commit/push [Task 2]

## Reusable knowledge

- Only 20250418_Final_20Report_EN.md mentions carbonsim (21 hits; other background files 0); Task5/6 section records EDF selection, VN translation, VND, and the 11 Oct 2023 internal training. VN parameters: cap 355.85Mt, 3 percent per year, 90 percent free, 4 auctions per year, 100/300 collar, 300+1 penalty, 10 percent offsets, 10 percent band, 242 units. [Task 1]
- Original stack verified live: MVC 5.2 on .NET 4.0/IIS10, SignalR 2.1.2, dygraphs 1.0.1, techan archived 2016, jQuery 1.11, Bootstrap 3.2; rebuild target chosen as .NET 10 LTS plus Core SignalR plus EF Core plus ECharts with Blazor Server. [Task 1]
- Public-vs-blocked inventory: /home/resourcestrings is public with 883 EN keys (translations auth-only), AvailablesCompanies lists 400 without PIN, login POST is 403, /admin redirects to login; behavioural spec only, legal limit recorded. vncarbonmarket.com is hijacked so use Wayback; ETP page is canonical. [Task 1]
- YouTube retrieval: yt-dlp needs node runtime plus --extractor-args youtube:player_client=android -f 18 (default client 403s, HD 720p/1080p unavailable); dedupe rolling captions to minute-stamped md and extract admin frames via ffmpeg plus thumbnail diff; key find is the Simulation Admin console surface (Reports, Leaderboard, Issue Fines, Auction, Exchange, End-of-Year Mods, Surrender Status, Disburse Offsets, Add Abatement, Server Admin; Begin Year/Disable Messaging/Stop). [Task 1]
- Numeric-fidelity framing: behavioural equivalence with Route1 owner outreach in parallel with Route3 first-principles bot plus envelope test suite and Route2 output inference (41 Dominican clears, Mexico totals, demo). Training Reports 1-3 are not online; only via ETP/UNOPS, VNEEC, or Josh. [Task 1]
- Builder orchestration that worked: create tab and pane, start herdr agent builder kind omp with the flash model, rephrase on Create Unsafe Agents denial (no installs), batch Phase0 plus entities/params/loader (52 green), then clock/RNG/allocation/abatement/auction/exchange/OTC (172 green), then reconciliation/finance/scoring/bots/fidelity (232 passed 4 skipped); spot-check Auction.cs clearing (price-then-time, floor if undersubscribed, per-vintage, reserve); instruct commit plus push to e85c910. [Task 2]

## Failures and how to do differently

- Firecrawl scrapes oversize -> save to tool-results files and grep via shell; a 212-byte Dominican PDF stub means keep the markdown and delete the stub. [Task 1]
- Company names initially copied from sim3 must be replaced with invented names; research is spec and never ships (lessons.md record 1). [Task 2]
- Long herdr agent prompt --wait calls get killed for low memory -> use Monitor with a sleep loop and never poll rapidly. [Task 2]
- git commit blocked by auto-mode Out-of-Place Publication -> narrow to git add of the intended paths; git push fails on wincredman/no-tty with gh auth failing -> leave push to a user terminal (gh auth login; git push origin main). [Task 1]

# Task Group: DPPA advisory fee benchmarks in reopt-pysam
scope: Research global PPA/DPPA advisor-fee evidence and write versioned benchmark briefs with a JSONL source ledger and recomputed Vietnam economics, reporting completion via Herdr prompt.
applies_to: cwd=C:\Users\tukum\Downloads\reopt-pysam; reuse_rule=repo-convention-sensitive (never hard-code FX; resolve via data/vietnam/vn_deal_defaults_2026.json); rerun wide_pass.py before deep reads on resume

## Task 1: DPPA advisory fee benchmark report v1, success

### rollout_summary_files

- rollout_summaries/2026-10-03T00-17-19-9KUA-dppa_advisory_fee_benchmarks_v1_and_v2_retry.md (cwd=C:\Users\tukum\Downloads\reopt-pysam, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\03\rollout-2026-10-03T07-17-19-01a0ff1f-56a5-7803-b60c-ed723f8d3fa4.jsonl, updated_at=2026-10-03T00:36:38+00:00, thread_id=01a0ff1f-56a5-7803-b60c-ed723f8d3fa4, v1 39KB with 62 sources done; exhaustive v2 retry aborted)

### keywords

- DPPA, PPA advisory fee, Schneider Zeigo, Vietnam Decree-57, PowerShell file write, node_repl blocked, herdr agent prompt, source ledger, FX never hard-coded

## Task 2: Exhaustive DPPA fee benchmark v2 with ledger, success

### rollout_summary_files

- rollout_summaries/2026-10-03T00-36-48-LedF-dppa_advisory_fee_benchmark_v2.md (cwd=C:\Users\tukum\Downloads\reopt-pysam, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\03\rollout-2026-10-03T07-36-48-01a0ff31-2f39-7750-8809-99b236655cdf.jsonl, updated_at=2026-10-03T00:58:23+00:00, thread_id=01a0ff31-2f39-7750-8809-99b236655cdf, 2pct fee judged consistent near USD 1/MWh; 422-row ledger with 105 cited sources)

### keywords

- DPPA, PPA advisory fee, Schneider Electric, LevelTen seller-pays, Decree 57, Vietnam, wide_pass.py, source ledger, exhaustive depth, VND-USD FX, econ_v2.py

## Task 3: Platform-level PPA/DPPA fee evidence brief v3 plus push, success

### rollout_summary_files

- rollout_summaries/2026-10-03T03-49-52-SBKS-ppa_platform_fee_evidence_v3.md (cwd=C:\Users\tukum\Downloads\reopt-pysam, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\03\rollout-2026-10-03T10-49-52-01a0ffe1-f0a2-7790-b2b6-bb3b6fbfaf1e.jsonl, updated_at=2026-10-03T04:32:04+00:00, thread_id=01a0ffe1-f0a2-7790-b2b6-bb3b6fbfaf1e, v3 brief 11412 bytes plus commit 7986e73 pushed)

### keywords

- PPA platform fee, LevelTen, Pexapark, Zeigo, Xpansiv, Evident I-REC, Ever.green, IEX, CRESS, VN_DEAL_DEFAULTS, apply_patch, Set-Content UTF8

## User preferences

- when reporting research, the user asked for output at `research/2026-10-03_dppa-advisory-fee-benchmarks.md` (create research/ if missing) with executive summary, benchmark table by region, and numbered source list (50 or more) -> default to that report shape without re-asking [Task 1]
- when complete, the user said report back by running `herdr agent prompt w3K:p1 "Codex feeresearch DONE: report at ... - <headline>, <N> sources."` then stop -> use that exact one-line completion signal [Task 1][Task 2]
- when writing files, the user corrected `Do NOT use the node_repl/js tool` and to use `apply_patch (Add File) or plain PowerShell here-string with Set-Content -Encoding utf8, in chunks if needed` -> avoid node_repl/js on this provider entirely [Task 1][Task 2]
- when v1 was judged too thin with author estimates and weak sources, the user said go much wider and deeper and "Do NOT reuse its estimates as evidence" -> hunt HARD fee numbers (public-sector RFPs/board minutes, seller-paid success/platform fee docs, filings, TA fees) and never promote estimates to verified [Task 2]
- when citing for benchmarks, the user requires 100 or more distinct credible sources with every cited URL pointing at the specific page/document (no homepages/topic pages), each fact tagged verified/estimate/thin, a regional table showing ONLY sourced numbers in the evidence column (estimates separate), recomputed economics, and an explicit unverifiable list [Task 2]
- when searching fee evidence, the user requires multilingual search including Vietnamese, Japanese, Korean, Chinese (Taiwan), Spanish, German (for example `phi tu van DPPA, mua ban dien truc tiep`) plus Decree 57/2025 mechanics and per-kWh DPPA charges [Task 2]
- when running exhaustive research, the user said use the $research skill with --depth exhaustive, follow its references/exhaustive.md and source-quality.md exactly, including wide_pass.py and the JSONL ledger -> use skill-mandated wide_pass.py plus JSONL ledger, never hand-roll retrieval [Task 2]
- when handling currency, the repo convention is that new code must never hard-code an FX literal and must resolve via data/vietnam/vn_deal_defaults_2026.json -> read FX live (26400 VND/USD seen) via helper/script, never hard-code [Task 2]
- when extending prior briefs, the user said read them first and do not repeat their content, extend it -> read research/2026-10-03_dppa-advisory-fee-benchmarks.md and -2.md first and add only new platform-doc evidence [Task 3]
- when requesting the platform sweep, the user said only sourced numbers in the number column plus every URL must be a specific page/document -> leave undisclosed cells as undisclosed, never infer numbers, cite specific pages not homepages [Task 3]
- when constraining tools, the user said firecrawl credits may be exhausted so fall back to other web tools, do not use node_repl/js, write files with apply_patch or PowerShell Set-Content -Encoding utf8, and run the exact one-line shell command then stop -> respect tool bans, UTF-8 write method, and exact completion ping format [Task 3]
- when the user said Git commit push main with no extra spec -> commit only the requested deliverable, leave other untracked work untouched [Task 3]

## Reusable knowledge

- Direct PowerShell writes work for long markdown: `Set-Content -Encoding utf8 -Path <report> -Value @'...'@` then repeated `Add-Content -Encoding utf8` in chunks; verified to build a 39124-byte report. v2 outputs are research/2026-10-03_dppa-advisory-fee-benchmarks-2.md (229 lines, 105 cited sources), research/sources/2026-10-03_dppa-advisory-fee-benchmarks-2.sources.jsonl (422 rows, 182 qualified tier 3 or better), and research/sources/econ_v2.py plus econ_v2.json. [Task 1][Task 2]
- 2pct-of-capex base case recomputed in-repo via econ_v2.py: 700 USD/kWp, CF 17.5pct, 9pct WACC 20y gives USD 1.00/MWh = VND 26.41/kWh; 20y band USD 0.856-1.251/MWh; validated against Skokie winner-pays and WoodMac dev-fee comparables. Headline used: 2pct developer-paid fee is within global norms at about 1 USD per MWh and contestable on floor, funnel and product rather than rate. [Task 2]
- Hard-fee anchors verified: LevelTen sellers-pay/buyers-free marketplace; Skokie SD68 IL solar RFP USD 0.07/W winner-pays; Orange NJ USD 30k winner-pays; WaveUp/Firmex M and A small-deal 2-8pct EV; WoodMac developer fees USD 0.20-0.60/W; IRENA 2024 TIC 691 USD/kW; EVN avg retail 2,204.064 VND/kWh May 2025; Samsung SEVT / TTC Duc Hue 2 about 70 GWh/yr first DPPA. [Task 2]
- Ledger triage rule that worked: OpenAlex unqualified queries flood academia with off-topic rows; filter by title regex (ppa|photovoltaic|solar|wind|renewable|energy|electricity|tariff|intermediation|broker|auction|procurement|project financ|development fee etc) and mark off-topic tier 5 rejected for an audit trail. Firecrawl credits exhausted is not run failure: fall back to environment web_search plus direct page opens for industry/web, re-verify hard-fee URLs, record the fallback reason, and reallocate shortfall to academia per skill default. [Task 2]
- wide_pass.py usage: `python -X utf8 <skill>/scripts/wide_pass.py --ledger research/sources/<name>.sources.jsonl --academia-target N --academia-query "..." --github-target N --industry-target N --web-target N`; create `research\sources` first. Research skill layout: C:/Users/tukum/.agents/skills/research/SKILL.md, references/exhaustive.md, references/source-quality.md, scripts/wide_pass.py. [Task 2]
- 2% capex base math recomputed live: CRF(9%,20y)=0.10955, 14000 USD/MWp * CRF = 1533.65 USD/yr / 1533 MWh/yr = 1.0004 USD/MWh ~26.4 VND/kWh; 9% CF low-yield ~1.95 USD/MWh ~51 VND/kWh. [Task 3]
- Sourced fee comparators: Xpansiv CBL 250 USD/user/month + 0.05 USD/unit retirement; Evident/I-REC 0.06-0.08 EUR/MWh + 0.025 platform + 300/1000 EUR device + 2000 GBP trader + from 1000 USD registrant; Ever.green ToS 7% of transaction fees via Baker Tilly; IEX 0.04 Rs/kWh + 40 Rs/certificate; UK brokers typical 0.05p-5p/kWh caps 1-2p/kWh; Malaysia CRESS 25->20->14 sen/kWh grid charge (not broker fee); Ofgem Oct-2024 is a disclosure rule with no numeric cap; LevelTen seller-pays direction only, no public pct. [Task 3]
- Interpretation: ~1 USD/MWh sits ABOVE pure registry tolls (~0.10 USD/MWh), BELOW UK broker uplifts (~6.5 USD/MWh at 0.5p), near IEX (~0.48 USD/MWh); outlier in BASE (capex vs energy) and TIMING (lump at signing developer-pays in buyer-side RFP). [Task 3]
- Remote-moved warning is non-fatal: push via the old tah-allotrope/reopt-pysam.git URL still succeeded to the new TukuCorp/reopt-pysam.git location (main 2fe19a1..7986e73). [Task 3]
- Related skill: skills/exhaustive-ledger-research/SKILL.md

## Failures and how to do differently

- `tools.apply_patch` with `*** Add File` plus `@@` hunks failed verification on this provider; pivot to PowerShell Set/Add-Content. `mcp__node_repl__js` / `btoa` are unavailable (provider rejected node_repl); go straight to PowerShell. [Task 1]
- Initial wide_pass academia queries that were too broad (for example corporate PPA transaction costs intermediation) yielded 300-plus mostly off-topic rows with only 143 relevant after triage; start with narrow fee-specific queries and triage early before appending industry/web. The github bucket is natively sparse for this topic (2 rows, both rejected); record the deficit and reallocate per skill default instead of padding with junk. [Task 2]
- `request_user_input_async` ratio prompts repeatedly failed to parse (invalid type map, unknown field header); when the user already implies an industry/web-heavy need, proceed with an explicit documented ratio instead of blocking on the prompt tool. PowerShell ternary `$env:X ? 'a':'b'` throws ParserError; use `if ($env:X){...}else{...}`. Python cp1252 decode errors need PYTHONIOENCODING=utf-8. append_v2.py generated with a JS-style loop failed; rewrite the loop in Python via Set-Content/Add-Content before execution. [Task 2]
- An exhaustive wide-pass exec aborted by the user leaves the ledger empty or partial; on resume, re-run wide_pass.py before deep reads, then write brief plus ledger in PowerShell chunks. [Task 1]
- apply_patch with Begin Patch / Add File plus markdown content and hunk headers failed twice with invalid hunk errors -> in this exec-tool environment apply_patch expects freeform input without git-style hunks; the pivot that worked was PowerShell Set-Content -LiteralPath -Encoding utf8 empty then chunked Add-Content (16 lines per call) to write the 11412-byte brief. [Task 3]

# Task Group: BIDV PCAF TypeSafe Jev crosswalk pipeline
scope: Build and validate a blind BIDV-to-PCAF code-matching pipeline and its phase handoffs without reading prior v0.x outputs through P3.
applies_to: cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb\bidv-fe-codes; reuse_rule=checkout-specific; preserve the stated blind-coding boundary and revalidate model/API behavior before reruns

## Task 1: Build and validate Jev matching pipeline, success

### rollout_summary_files

- rollout_summaries/2026-09-29T03-55-02-MPDZ-bidv_pcaf_jev_crosswalk_p0_p5.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb\bidv-fe-codes, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\29\rollout-2026-09-29T10-55-02-01a0eb4d-3b37-7ba3-b0bb-1fac6b43558b.jsonl, updated_at=2026-09-29T04:18:48+00:00, thread_id=01a0eb4d-3b37-7ba3-b0bb-1fac6b43558b, 587/587 classification and 12 tests passed)

### keywords

- typesafe-sdk, jev-1.13.0, BIDV_PCAF_crosswalk_v1.0-jev.xlsx, jev_match.py, Noul, output/jev_cache, 46310A, G46310A, 587/587, 12 passed

## Task 2: Produce phase handoff/reporting artifacts, success

### rollout_summary_files

- rollout_summaries/2026-09-29T03-55-02-MPDZ-bidv_pcaf_jev_crosswalk_p0_p5.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb\bidv-fe-codes, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\29\rollout-2026-09-29T10-55-02-01a0eb4d-3b37-7ba3-b0bb-1fac6b43558b.jsonl, updated_at=2026-09-29T04:18:48+00:00, thread_id=01a0eb4d-3b37-7ba3-b0bb-1fac6b43558b, P0-P5 handoffs completed)

### keywords

- handoff/jev_reply_P0.md, jev_reply_P5.md, Review queue, Compare vs v0.9, README, output/jev_results.json

## Task 3: Summarize pacta-trisk recent progress, success

### rollout_summary_files

- rollout_summaries/2026-09-29T21-22-45-Sb85-pacta_trisk_recent_progress_sep_2026.md (cwd=C:\Users\tukum\Downloads\pacta-trisk, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T04-22-46-01a0ef0c-7379-7fb3-9607-1a7c7343ff91.jsonl, updated_at=2026-09-30T01:18:39+00:00, thread_id=01a0ef0c-7379-7fb3-9607-1a7c7343ff91, tracked main quiet since 2026-09-13; active untracked gtb/bidv-fe-codes work)

### keywords

- pacta-trisk, git log, git status, gtb, bidv-fe-codes, artifact-catalog, Wave 5, progress summary, untracked

## User preferences

- when the user required "Do not stop between phases unless blocked." -> continue planned phases and write the required handoff reply after each phase [Task 1][Task 2]
- when the user required independent/blind coding through P3 and prohibited reading prior outputs/code -> preserve that blindness boundary in matching runs [Task 1]

## Reusable knowledge

- Confirm `typesafe-sdk` and make a live smoke call before the full run. This run used `jev-1.13.0`, a BEA hierarchy with beam width K=3, async retries, `output/jev_cache/`, geometric-mean path scores, separation, Noul verification, and H/M/L tiers. [Task 1]
- The completed run classified 587/587 rows with 2,634 API calls, 42 cache hits, and 94.5 seconds; verification made 695 Noul calls in 25.6 seconds, yielding H=243, M=247, L=97, 108 top-2 verifications, and 39 close calls. [Task 1]
- Outputs are `output/BIDV_PCAF_crosswalk_v1.0-jev.xlsx`, `output/jev_results.json`, `jev_match.py`, `test_jev_match.py`, `jev_compare.py`, and `jev_write.py`; `python -m pytest test_jev_match.py -q -p no:cacheprovider` passed 12/12. [Task 1]
- Against v0.9, exact agreement was 459/587 (78.2%), same group 93.7%, same EF band 87.9%, Iκ exact 0.7802, and Iκ EF-band 0.8437. The workbook has `Crosswalk`, `Review queue`, `Compare vs v0.9`, and `README` sheets. [Task 1][Task 2]

## Failures and how to do differently

- If `llms.txt` or cookbook examples fail, use SDK introspection plus a live smoke call to establish the API shape. [Task 1]
- Inline PowerShell/Python quoting caused syntax errors; switch to script files. Large patch fragments were unreliable; assemble verified file parts on disk instead. [Task 1]
- P4 initially missed v0.9 key `46310A`; inspect normalized and original code columns and alias normalized codes such as `46310A` -> `G46310A` before joining. [Task 1]
- Efficient progress-check pattern in this repo: `git log --oneline -20 --date=short --format='%h %ad %s'` plus `git status --short --branch` plus PowerShell Get-ChildItem sorted by LastWriteTime, then a second pass `git log -5 --stat --oneline` with listings of `gtb/` and `reports/`. Tracked `main` was quiet since 2026-09-13 as of 2026-09-30 (last commits f9842ec artifact catalog close, 8e0d4de, bd09f48 Wave 5 gate); the active newest work was untracked in `gtb/bidv-fe-codes/` (crosswalk prototype, v0.9 results, Jev matching pass, BIDV_PCAF_crosswalk_v1.0-jev.xlsx). Inspect both tracked log and untracked recent files from the start. [Task 3]

# Task Group: Personal Google Drive-to-Photos transfer and local cleanup
scope: Download a shared Drive folder, transfer media to personal Google Photos, and clean up local copies without losing known upload failures.
applies_to: cwd=C:\Users\tukum\Downloads\remote\personal; reuse_rule=account and transfer-specific; reauthenticate, re-enumerate, and verify every source item before deletion

## Task 1: Download ASEAN Drive folder and upload media to personal Photos, partial

### rollout_summary_files

- rollout_summaries/2026-09-29T04-16-28-5tru-drive_photos_upload_cleanup_herdr_paint.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\29\rollout-2026-09-29T11-16-28-01a0eb60-da37-7331-9935-669c5c8e2784.jsonl, updated_at=2026-09-29T13:59:14+00:00, thread_id=01a0eb60-da37-7331-9935-669c5c8e2784, 1,408/1,409 media uploaded)

### keywords

- gws, Google Drive, Google Photos, ASEAN, PowerShell quoting, Python subprocess, alt=media, supportsAllDrives, Photos Library API, asean night 079.mov

## Task 2: Delete local transfer and create a fun painting, mixed

### rollout_summary_files

- rollout_summaries/2026-09-29T04-16-28-5tru-drive_photos_upload_cleanup_herdr_paint.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\29\rollout-2026-09-29T11-16-28-01a0eb60-da37-7331-9935-669c5c8e2784.jsonl, updated_at=2026-09-29T13:59:14+00:00, thread_id=01a0eb60-da37-7331-9935-669c5c8e2784, local folder deleted; Paint launch unverified)

### keywords

- Remove-Item -LiteralPath, Test-Path, 1453 files, 2.77 GB, fun2.png, Microsoft.Paint_8wekyb3d8bbwe, file://

## User preferences

- when the user asked to download "directly into the current folder" -> preserve the source folder hierarchy and execute in the requested location [Task 1]
- when the user chose `personal` for Photos then said "just simply report that you're done, no need further context." -> use the selected account and keep the completion response brief, while still reporting a known incomplete upload if one remains [Task 1]

## Reusable knowledge

- The installed `gws` CLI expects JSON through `--params`. If nested PowerShell quoting produces `Invalid --params JSON: key must be a string`, invoke `gws` from a Python argument array with `json.dumps(params)`. [Task 1]
- For Drive folder downloads, query `'FOLDER_ID' in parents and trashed=false` with `supportsAllDrives=true`, `includeItemsFromAllDrives=true`, binary `alt=media`, and idempotent skip-existing retries. This transfer completed 34 folders and 1,453 files with two timeout retries. [Task 1]
- Before local cleanup, compare the enumerated upload set against Photos results item by item, including failed media. `Test-Path` verifies deletion only, not cloud completeness. [Task 2]

## Failures and how to do differently

- The transfer deleted the local folder while `asean night 079.mov` still failed Photos media-item creation. Do not claim a complete transfer or delete the only local original until every item is uploaded or separately preserved. [Task 1][Task 2]
- Photos album creation returned `{id,title,...}`, not a nested `album` object. Enable the Photos Library API after a 403 API-disabled error, then handle that response shape. [Task 1]
- Paint immediately exited because of corrupted Microsoft Paint settings, and browser Computer Use rejected `file://` URLs. Treat the generated `fun2.png` as verified only by file/image checks, not as proof that Paint opened it. [Task 2]

# Task Group: TypeSafe Jev use-cases and multi-agent laptop setup
scope: Rank Jev use-cases from live GitHub repos plus TypeSafe docs, then install the TypeSafe skill, SDK, and API key for Claude Code, opencode, Hermes, and omp with per-agent verification.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=laptop-wide setup procedure (paths and env vars are machine-specific); repo-fit rankings are time-specific

## Task 1: Suggest Jev use-cases from GitHub repos and TypeSafe docs, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-1yKv-typesafe_jev_use_cases_and_multi_agent_setup.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b09f-7d61-9eb8-460e2a4c2fc3.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b09f-7d61-9eb8-460e2a4c2fc3, ranked fits with ruled-out poor fits; live Noul test 1.0)

### keywords

- typesafe, jev-latest, TYPESAFE_API_KEY, typesafe-sdk, Noul, Choice, Score, gh api user/repos, TukuCorp, pacta-trisk, pdd-auto, skills.sh, hermes .env

## Task 2: Set up TypeSafe skill, SDK, and API key for four agents, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-1yKv-typesafe_jev_use_cases_and_multi_agent_setup.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b09f-7d61-9eb8-460e2a4c2fc3.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b09f-7d61-9eb8-460e2a4c2fc3, key stored to User env plus Hermes .env; rotation advised since transcript holds the secret)

### keywords

- claude plugin typesafe, npx skills add, hermes-agent, universal, omp skills, TYPESAFE_API_KEY, Read-Host AsSecureString, console.typesafe.ai, HERMES_HOME

## User preferences

- when asking for repo-grounded suggestions, the user said: "Check my github repos and jev docs to suggest some use case for my work if any" -> ground suggestions in actual repo READMEs plus TypeSafe primitives and cookbooks, rank by fit, and explicitly rule out poor fits [Task 1]
- when asking for multi-agent setup, the user said: "setup on this laptop for me so claude code, hermes, omp, opencode can all use" -> cover all four surfaces by default and report per-agent paths plus verification separately [Task 2]

## Reusable knowledge

- GitHub identity is tah-allotrope (keyring); work lives in TukuCorp and tukumalu orgs. When gh repo list returns empty, use gh api "user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=updated" then per-repo gh api repos/TukuCorp/<repo>/readme. [Task 1]
- Jev is a System One model with no text generation: Choice, Score, and Noul typed questions against state, run in parallel with probabilities plus confidence. Best for classification, matching, and checking messy text; poor fit for calculation-heavy repos (dss-grid, reopt-pysam, ee-heat, RE-storage-model, carbonsim). Top ranked fits were pacta-trisk entity-alignment plus sector tagging plus PCAF scores on synthetic data, Hermes skill-suggestion plus intent-routing, and pdd-auto Noul/Choice review checks with confidence-gated routing; prototype on synthetic data first and check TypeSafe retention for confidential data. [Task 1]
- Claude Code setup is claude plugin marketplace add typesafe-ai/skills plus claude plugin install typesafe@typesafe-ai (user scope; invoke via /typesafe:typesafe-ai). Other agents go through npx skills add typesafe-ai/skills with agent flags; valid agent names surface in the error when a bogus name is tried. Installed copies land at ~/.agents/skills/typesafe-ai (opencode shared), %LOCALAPPDATA%/hermes/skills/typesafe-ai (Hermes active dir), and ~/.omp/agent/skills/typesafe-ai for omp; omp keeps skills under ~/.omp/agent and ~/.pi was an installer artifact removed after moving its skill. [Task 2]
- Python SDK is python -m pip install typesafe-sdk with env var TYPESAFE_API_KEY, default model jev-latest, default URL https://api.typesafe.ai; gateway and long-running processes need a restart to see new env. Hermes keys live in ~/AppData/Local/hermes/.env, so back it up before editing, keep the trailing newline, and never edit cron/jobs.json directly while the gateway runs. [Task 2]

## Failures and how to do differently

- A pasted API key in chat survives in the transcript -> after storing it to User env plus Hermes .env and verifying live, tell the user to rotate it at console.typesafe.ai and re-supply via hidden input. [Task 2]
- Do not restart the Hermes gateway unprompted when pipeline crons are running; leave the restart to the user between runs. [Task 2]




# Task Group: Fable model credit spend advice from repo sweeps
scope: Ground model-spend advice in local clone inventories plus GitHub repo listings, with exact pricing math and worth/not-worth splits; fix pricing tables before any paid run.
applies_to: cwd=C:\Users\tukum\Downloads\remote\personal; reuse_rule=sweep-procedure reusable (gh repo list plus local .git find plus per-clone stats); re-enumerate repos on each run, prices change

## Task 1: Local repo plus Fable 5.1 capability advice, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-EyGo-fable_5_1_credit_repo_sweep_advice.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b8b6-7411-b808-edbc364d1b5c.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b8b6-7411-b808-edbc364d1b5c, Fable specs plus 100-dollar math plus worth/not-worth split)

### keywords

- Fable 5.1, 100 credit, remote-data, git repos, capability advice, effort, cache, Batch, INDEX.md

## Task 2: Wider GitHub repos check for Fable use cases, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-EyGo-fable_5_1_credit_repo_sweep_advice.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b8b6-7411-b808-edbc364d1b5c.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b8b6-7411-b808-edbc364d1b5c, 25 GitHub repos plus 24 local clones; pricing bugs found)

### keywords

- gh repo list, local clones, workflow-bench, agent-evals, pdd-auto, model_pricing.yaml, roster.yaml, stale pricing

## User preferences

- when asking for model advice, the user said check git repos and Fable 5.1 capability to advise effective 100-dollar credit use -> give repo-grounded, capability-specific spend advice, not a generic model description [Task 1]
- when the initial answer covered only the local repo, the user said conduct a wider check on GitHub repos -> enumerate exhaustively across GitHub plus local clones [Task 2]

## Reusable knowledge

- remote-data is a business-ops knowledge base with daily 05:02 auto-backup; live 30-day work sits in hp/cpi/copper/ceba/gtb/apps-script; 30-day retention is a governance issue for signed govt letters, financials, CVs, and NDAs in temp/. [Task 1]
- Fable 5.1: 10 in / 50 out, 0.25 cache reads, 1M context, 128K out; thinking always-on via effort low->max is the biggest cost lever; no Priority Tier; Batch halves price; 100 dollars is about 75 red-team memo passes or 20 folder analyses, never a whole-corpus pass (~50). [Task 1]
- Sweep commands: gh repo list --limit 100 with json fields for the GitHub side; maxdepth-3 .git find for local clones; per-clone last-commit date, commit count, file count, README headline, and LLM-API hits. [Task 2]
- Pricing bugs found: sonnet-5 3/15 vs actual 2/10, opus-4-8 15/75 vs 5/25, haiku 0.25/1.25 vs 1/5, missing opus-5 5/25 and fable 10/50; pdd-auto cost guard has no Fable rate and duplicates pricing in two files with no cache tier. [Task 2]

## Failures and how to do differently

- Broad grep across the repo timed out at 120s and backgrounded; scope sweeps to subdirs with timeout 100. Do not trust INDEX.md for deletions; verify via git show --stat (hp/ was deleted in 2c9adaf). [Task 1]
- workflow-bench roster cells invoke CLIs, so spend may hit subscription not API credit; confirm or add an API-direct cell before spending. Fix pdd-auto pricing plus cache tier before any paid run or BudgetExhaustedError bills wrong by up to 40x. [Task 2]

# Task Group: Emerald Emberleaf ROM-hack preparation
scope: Prepare and verify a user-owned Pokemon Emerald first-town and Route 101 hack; distinguish validated drafts and committed workspace from a playable ROM.
applies_to: cwd=C:\Users\tukum\Downloads\rom-hack; reuse_rule=checkout-specific; only build from a user-owned compatible US v1.0 Emerald dump and do not acquire commercial ROMs

## Task 1: Prepare town and Route 101 hack, partial

### rollout_summary_files

- rollout_summaries/2026-09-28T08-48-51-mn5p-emerald_hack_prep_and_blocked_rom_build.md (cwd=C:\Users\tukum\Downloads\rom-hack, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T15-48-52-01a0e733-df3a-7500-b9c5-f0c31c805dfb.jsonl, updated_at=2026-09-28T14:13:01+00:00, thread_id=01a0e733-df3a-7500-b9c5-f0c31c805dfb, drafts validated; playable ROM not built)

### keywords

- pokeemerald, Emberleaf, Route101, Coral Path, baserom.gba, Porymap, mGBA, MSYS2, RUNBOOK.md, 79f77f8

## Task 2: Build and verify standalone Shield battle demo, success

### rollout_summary_files

- rollout_summaries/2026-09-27T19-38-56-lDmi-standalone_pokemon_shield_battle_demo.md (cwd=C:\Users\tukum\Downloads\rom-hack, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T02-38-59-01a0e460-aedd-7b72-81fd-5e4a64b6247a.jsonl, updated_at=2026-09-27T20:08:53+00:00, thread_id=01a0e460-aedd-7b72-81fd-5e4a64b6247a, browser-verified standalone demo)

### keywords

- shield-battle, index.html, Cinderace, Corviknight, Dynamax, canvas, server.py, projectile timers, hidden CSS, Pyro Ball

## Task 3: Orient workspace and give msys2 non-WSL build path, success

### rollout_summary_files

- rollout_summaries/2026-10-02T09-06-43-lDyt-emerald_rom_hack_setup_msys2_baserom_verify.md (cwd=C:\Users\tukum\Downloads\rom-hack, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\02\rollout-2026-10-02T16-06-44-01a0fbdd-abae-7ed0-a13a-23cd5b05febd.jsonl, updated_at=2026-10-04T07:36:53+00:00, thread_id=01a0fbdd-abae-7ed0-a13a-23cd5b05febd, orientation plus msys2 path plus zip/toolchain sizes; no build run)

### keywords

- emerald-decomp, INSTALL.md, msys2, devkitARM, msys2_shell.bat, pacman, baserom.gba, sha1sum, make check, porymap.exe, mGBA.exe, ruby-hoenn

## Task 4: Verify existing ROM zip sizes and propose slim msys2 toolchain, success

### rollout_summary_files

- rollout_summaries/2026-10-02T09-06-43-lDyt-emerald_rom_hack_setup_msys2_baserom_verify.md (cwd=C:\Users\tukum\Downloads\rom-hack, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\02\rollout-2026-10-02T16-06-44-01a0fbdd-abae-7ed0-a13a-23cd5b05febd.jsonl, updated_at=2026-10-04T07:36:53+00:00, thread_id=01a0fbdd-abae-7ed0-a13a-23cd5b05febd, zip verified usable as baserom; slim toolchain proposed, nothing installed)

### keywords

- Emerald zip, 6791457 bytes, inner SHA1 match, baserom.gba, 308.9MB, slim msys2, arm-none-eabi-binutils, agbcc, make modern

## User preferences

- when the user said "don't install anything dud, revert" after an unsolicited MSYS2 attempt -> never install system software without explicit approval; confirm the scope and rollback plan first [Task 1]
- when the user asked "Get rom with browser use" -> explain briefly that a commercial ROM cannot be acquired; give instructions for the user's own compatible dump [Task 1]
- when the user requested "git commit push main/master" -> commit and push the requested project changes, preserving unrelated untracked work [Task 1]
- when the user required a demo "independent of other demos" and "great visual commercial grade" -> use an isolated directory and original assets/source; deliver presentation polish and rendered interaction verification, not mechanics alone [Task 2]
- when the user asked "what do i need to do to hack rom now" with no other spec -> inventory the existing workspace docs and plans first, then give workspace-grounded next steps rather than generic instructions [Task 3]
- when the user asked "anyway to proceed without wsl?" -> prefer a native Windows path and avoid a WSL install when the setup question allows it [Task 3]
- when the user said there should be a zip rom already and asked how big the installation is -> give measured sizes and verify the existing download is usable, not estimates [Task 4]
- when the user asked why the toolchain is so big and whether a lighter package exists -> distinguish measured vs estimated sizes and give a slim install covering only needed targets [Task 4]

## Reusable knowledge

- The required base is `emerald-decomp/baserom.gba`, a user-owned clean US Emerald v1.0 dump with SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`. `emerald-town-route/RUNBOOK.md` orders SHA-1 check, `make check`, draft application, build, playtest, graphics, then `.ups` packaging. [Task 1]
- Validated drafts live in `emerald-town-route/draft/`: dialogs, 12 Route 101 encounters, environment names, cast/lab swaps, and graphics plan. Binary layout files `data/layouts/*/map.bin` and `border.bin` need Porymap, not text edits. [Task 1]
- New overworld NPCs need sprite sheet and palette, pic table, graphics-info struct, graphics ID/pointer, and map `graphics_id` updates. The workspace was pushed to `main` as `79f77f8`. [Task 1]
- `shield-battle/index.html` is a standalone single-file Cinderace-vs-Corviknight battle demo with procedural canvas art, WebAudio, turn order, STAB/effectiveness/crits/accuracy, Dynamax/Max moves, HP tweening, fainting, and rematch. Serve with `python server.py` and verify at `http://localhost:8000/shield-battle/index.html`; the live HTTP check returned 200. [Task 2]
- Workspace root holds `emerald-decomp/` (pret pokeemerald clone), `emerald-town-route/` (PLAN.md, RUNBOOK.md, GETTING-ROM.md, draft/, tools/), and `ruby-hoenn/` (no-ROM browser demo, entry `js/data.js`, `play-demo.bat` serves `python ..\server.py 8000`). Staged Windows tools: `emerald-town-route/tools/porymap/porymap.exe` and `emerald-town-route/tools/mgba/mGBA-0.10.5-win64/mGBA.exe`. [Task 3]
- Real Emerald build order: `sha1sum baserom.gba` must match `rom.sha1` (`f3ae088181bf583e55daf962a92bb46f4f1d07b7`), then `make check -j$(nproc)` for a byte-identical `pokeemerald.gba`, tag `baseline-clean`, then apply `emerald-town-route/draft/` text-only changes and ship as `.ups` patch only. [Task 3]
- Official non-WSL path per `emerald-decomp/INSTALL.md` is msys2 (about 2x slower than WSL1; skip Cygwin): install devkitPro GBA Development, open `C:\devkitPro\msys2\msys2_shell.bat`, run `pacman -Sy msys2-keyring` plus `pacman -S make gcc zlib-devel git` and libpng 1.6.37, then `make check` in `emerald-decomp/`; `baserom.gba` is still required. [Task 3]
- emerald-decomp/Pokemon - Emerald Version (USA, Europe).zip is 6.5MB (6791457 bytes) containing a 16.0MB GBA whose inner SHA1 f3ae088181bf583e55daf962a92bb46f4f1d07b7 matches rom.sha1, so it is usable as baserom.gba via Expand-Archive then Move-Item. [Task 4]
- Whole rom-hack/ is about 308.9MB across 11930 files (emerald-town-route 96.5MB, emerald-decomp 47.6MB, sunmoon 25.4MB); the biggest single file is the unrelated SoulSilver NDS at 128MB. [Task 4]
- The repo 7zr.exe cannot list that .zip (exit 1 despite PK header); use Python zipfile plus hashlib.sha1 streaming instead, then delete helpers. [Task 4]
- Makefile matching build (MODERN=0) uses tools/agbcc plus only arm-none-eabi-as/ld/objcopy/objdump and never devkitARM GCC, so the slim path is upstream MSYS2 plus pacman -S make gcc git zlib-devel arm-none-eabi-binutils plus libpng plus pacman -Sc (few hundred MB estimate); full devkitARM stays the fallback, and make modern still needs full GCC. Label estimates explicitly: the initial 1-3GB was a rough estimate, not measured. [Task 4]

## Failures and how to do differently

- No `baserom.gba` appeared, so no baseline build, patch, graphics edit, playtest, or `.ups` output exists. Do not call the drafts a playable ROM. [Task 1]
- An unapproved `winget` MSYS2 install failed and left protected `C:\msys64` leftovers. Do not attempt machine-wide installation or cleanup without approval. [Task 1]
- `emerald-decomp` was initially added as an embedded repository. Remove nested `.git` metadata only with appropriate permissions, then commit source as ordinary files rather than an embedded-repository pointer. [Task 1]
- Ranged shots soft-locked until projectile timing was initialized: initialize it for every new projectile and test every ranged move. CSS `display:grid` can override native `hidden`; retain `[hidden]{display:none}` or avoid forced display. Verify through HTTP rather than file URLs; AudioContext autoplay warnings are expected before user input. [Task 2]
- Complex PowerShell quoting through the exec wrapper failed twice (Select-String ParserError `The string is missing the terminator`, python SyntaxError on escaped quotes). Prefer simple `Get-Content` plus `Select-String -Pattern` with minimal quoting, or read INSTALL.md sections via narrow patterns. [Task 3]
- Inline `python -c` with quoted Windows paths fails in this exec wrapper; write a temp .py via apply_patch then run `python file.py` and delete after. Slim msys2 setup covers only matching `make check`: if the slim build errors, install full devkitARM before deep debugging. [Task 3][Task 4]

# Task Group: ee-heat project orientation and supplier prioritisation
scope: Give a direct, repository-grounded orientation for Allotrope Partners x Gap clean-energy work and route follow-up work to the current pipeline and context files.
applies_to: cwd=C:\Users\tukum\Downloads\ee-heat; reuse_rule=checkout-specific; recheck git state, reports, and active context before reporting current status

## Task 1: Explain repository purpose, structure, and current work, success

### rollout_summary_files

- rollout_summaries/2026-09-28T03-21-38-pgzx-ee_heat_project_overview.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T10-21-38-01a0e608-4c17-71f2-b2ba-10c6790523a3.jsonl, updated_at=2026-09-28T03:30:30+00:00, thread_id=01a0e608-4c17-71f2-b2ba-10c6790523a3, repository orientation)

### keywords

- ee-heat, Gap, clean heat, activeContext.md, lessons.md, pipeline/score, jev.py, composite.py, pipeline/gap_data, supplier prioritisation

## Task 2: Tay Ninh v1 snippet verification with 149 sources, success

### rollout_summary_files

- rollout_summaries/2026-09-30T12-21-51-THGF-tay_ninh_verification_v1_v2_browser_r3.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T19-21-54-01a0f243-981a-7012-87f6-3f01c1ac48f9.jsonl, updated_at=2026-10-01T04:30:29+00:00, thread_id=01a0f243-981a-7012-87f6-3f01c1ac48f9, v1 plus v2 plus browser pass plus round-3 expansion)

### keywords

- tay-ninh, hantex, top-sports, v1 snippet verification, 149 sources, site-findings html

## Task 3: Tay Ninh v2 industry-grade Tier A-C verification, partial

### rollout_summary_files

- rollout_summaries/2026-09-30T12-21-51-THGF-tay_ninh_verification_v1_v2_browser_r3.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T19-21-54-01a0f243-981a-7012-87f6-3f01c1ac48f9.jsonl, updated_at=2026-10-01T04:30:29+00:00, thread_id=01a0f243-981a-7012-87f6-3f01c1ac48f9, honest shortfall stated: 29 Tier A-C docs at that point)

### keywords

- Tier-A-B-C, open-and-read, 2019-2026, verdicts, link-check, self-audit, firecrawl 402, fitz, QCVN-19-2024, Decree-57

## Task 4: Browser bot-wall pass plus round-3 expansion to 50 Tier A-C docs, success

### rollout_summary_files

- rollout_summaries/2026-09-30T12-21-51-THGF-tay_ninh_verification_v1_v2_browser_r3.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T19-21-54-01a0f243-981a-7012-87f6-3f01c1ac48f9.jsonl, updated_at=2026-10-01T04:30:29+00:00, thread_id=01a0f243-981a-7012-87f6-3f01c1ac48f9, 50 distinct Tier A-C 25/13/12 with QCVN fix and scratch move)

### keywords

- browser-control, bot-wall, Wayback, WDS, OpenAlex, WP-JSON, QCVN 2032 fix, scratch gitignore, herdr agent prompt, IEA heat pumps, JRC BREF

## Task 5: Autonomous architecture review plus Strong-candidates plan, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-FkQF-ee_heat_architecture_review_and_refactor_plan.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b87c-7201-a08f-c203d77cc209.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b87c-7201-a08f-c203d77cc209, HTML review plus 747-line 25-task 3-phase plan; no code changes)

### keywords

- codebase review, architecture review, schema seam, stage runner, field_schema, pipeline registry, cli all, K-column collision, plans

## Task 6: Commit-push fe7c10a plus remote migration to TukuCorp, success

### rollout_summary_files

- rollout_summaries/2026-10-06T08-20-01-db7r-ee_heat_commit_push_update_remote.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T15-20-02-01a1104c-5ad4-7d82-b03c-2fc09dd6e0c1.jsonl, updated_at=2026-10-06T08:43:38+00:00, thread_id=01a1104c-5ad4-7d82-b03c-2fc09dd6e0c1, 25 files committed as fe7c10a and pushed; remote migrated to TukuCorp)

### keywords

- fe7c10a, TukuCorp remote, selective staging, reports redacted-only, pint missing, Get-ChildItem, git remote set-url

## User preferences

- when the user asked "tell me abt the projct" again after aborting a first attempt -> give a direct, practical overview grounded in the repository; lead with purpose, scope boundaries, current work, and unresolved issues [Task 1]
- when the user says only "git commit push main" over a broad dirty tree with confidential-adjacent files -> stage safe tracked plus new code/tests/decks/plans and deliberately leave supplier/site-identifiable reports unstaged for explicit opt-in [Task 6]
- when a persistent goal spans turns, keep the full objective intact and audit requirements against current state before marking complete; do not shrink scope to the easy subset [Task 2]
- when asked for industry-grade verification, the user said "open and read every source (no snippet-only citations, no search-result IDs), at least 100 Tier A-C 2019-2026 with real URLs, years and page refs, verdict for every claim, link-check every URL, do not overwrite v1. Never fabricate; if short of 100 say so" -> fetch full docs, record page/section/quote, keep v1 untouched, and state an honest shortfall [Task 3]
- when blocked on verification reporting, the user said report back with a single `herdr agent prompt w3E:p2 "..."` with no --wait and no other messages -> use exactly that cadence [Task 3]
- when asked for round-3 expansion, the user said "at least 50 distinct Tier A-C (same rules, no relaxing), reached by different routes" plus QCVN fix and scratch move -> diversify routes (gap-driven second sources, refs/OpenAlex snowballing, WDS/UNEP/LBNL/NREL/IEA/Unpaywall APIs, Vietnam/ASEAN repos, Wayback), never relax standards [Task 4]
- when codebase review was requested without review or input, the user said proceed alone to draft a plan for things worth resolving -> run fully autonomous execution (load vocabulary, scan hot spots, produce report, draft plan) without stopping for input; after review, draft a standalone versioned doc under plans/ covering only Strong candidates plus verified defects [Task 5]

## Reusable knowledge

- The repository supports Allotrope Partners x Gap Inc. work for Vietnam and Indonesia suppliers. Tung's scope is energy efficiency and clean heat; solar, BESS, and off-site DPPA are Rob's workstream. [Task 1]
- Start orientation with `activeContext.md`, `lessons.md`, `gap/MANIFEST.md`, recent `reports/`, then `pipeline/score/`. `jev.py` caches evidence judgments while `composite.py` applies policy weights, so weights can change without rerunning inference. [Task 1]
- `pipeline/gap_data/` is a separate hardcoded FDM path using Higg-ID identity and import-time file I/O. Its integration into the site store remains unresolved. Context reported 100 tests under Python 3.11; system Python 3.14 lacks `pint`. [Task 1]
- `pipeline/gap_data/` is a separate hardcoded FDM path using Higg-ID identity and import-time file I/O. Its integration into the site store remains unresolved. Context reported 100 tests under Python 3.11; system Python 3.14 lacks `pint`. [Task 1]
- v2 tier rules: Tier A multilateral/government/standards (IEA/IRENA/UNIDO/UNEP/World Bank/ADB/GIZ/DEA/US DOE/LBNL/NREL/JRC BREF/MOIT/EVN/ISO/ASHRAE), Tier B industry programmes (Aii/Cascale/ZDHC/SBTi/WRI/GHG Protocol/Fashion Charter/BSR/WRAP/Textile Exchange/Carbon Trust/EHPA/VITAS), Tier C peer-reviewed with DOI; Tier D corroboration only and not counted; banned are manual-dump/Scribd/marketplace/SEO/patents-as-performance/snippets. Deliverables are the v2 md plus tay-ninh-verification-v2-sources.csv (n,tier,org,year,title,url,http_status,claims_supported,quote) with link-check plus self-audit (tiers, years, duplicates, publisher cap 10 or fewer, Vietnam/SEA 15 or more). [Task 3]
- Browser-control pattern that beat the walls: `browser-control status`, session new, `--file scripts/bc/*.js` with Playwright `page.goto({waitUntil:domcontentloaded})` plus innerText plus link harvest; Cloudflare challenge needs waitForTimeout 8s then re-read; stale Debugger-not-attached means a new session. Key wins were IEA Future of Heat Pumps (500Mt, 3-5x, 140-160C), JRC TXT BREF Jan 2023 1029pp via EU-BRITE (p.702 airflow ratios), signed QCVN 19:2024 28pp plus CongBao Circular 45/2024 (issued 2024-12-30, effective 2025-07-01) with no 2032 clause in the QCVN text itself, Decree 57/2025 full text via vbpl, SBTi Criteria V5.3.1 plus Net-Zero V1.3.1. [Task 4]
- Repository APIs that worked: World Bank WDS `search.worldbank.org/api/v2/wds?format=json` (documents dict, docna to pdfurl), OpenAlex `api.openalex.org/works?filter=cites:WID` for cited-by, WP-JSON `wp-json/wp/v2/search` plus type endpoints for ESP/VEPG/ACEEE; ERIA/ESP/VEPG direct PDF download works. Final count 50 distinct Tier A-C (25/13/12), 62 rows all HTTP 200, verdicts 19/27/0/0/18, VN/SEA 22/50. [Task 4]
- Related skill: skills/exhaustive-ledger-research/SKILL.md
- Pipeline map: cli.py imports ingest/runner and validate/runner into core/stages (global registry) into core/cache (sha payload); only 2 stages exist; models/score/render empty; gap_data/ untracked bypasses everything; field_schema.yml 427 lines re-parsed 4x with 2 REPO_ROOT conventions; template.py duplicates rows 122-127 as Python literal. [Task 5]
- 7 candidates ranked: 1 schema seam (Strong), 2 declared-inputs cache (Strong, top recommendation first), 3 cli+registry collapse (Strong), 4 Site store / 5 gap_data fold / 6 Vietnam Context module (Worth exploring), 7 deck globals (Speculative); phase order is field_schema.py, then registry.py, then declared-inputs cache. [Task 5]
- Interpreter pin: tools/.venv/Scripts/python.exe Python 3.11.15 required; system Python 3.14 lacks pint. Always probe the synthetic workbook EX-001_returned.xlsx before specifying Unit/Source handling (K-column collision: K8 is longitude 106.82, K50 is efficiency share). [Task 5]
- Commit fe7c10a "CEBA EE deck v2.3/v2.4 with build updates, pipeline score and gap_data modules, tests, context and lessons": 25 files, 4880 insertions; v2.3/v2.4 pptx ~5.8MB each match the tracked v1-v2.2 pattern. reports/ history stays redacted/generic-only; 19 reports/ files (builders, combined-supplier xlsx, Gap/Tay Ninh html/md, sources csv) held back for explicit opt-in. Canonical remote is https://github.com/TukuCorp/ee-heat.git (the old tah-allotrope URL redirects with a warning but still pushes; update via git remote set-url origin then fetch to verify). [Task 6]

## Failures and how to do differently

- Do not give a generic overview after an interrupted start. Inspect the key context files and current report before answering, and flag untracked `pipeline/score/` and `pipeline/gap_data/` rather than treating them as committed project state. [Task 1]
- Do not give a generic overview after an interrupted start. Inspect the key context files and current report before answering, and flag untracked `pipeline/score/` and `pipeline/gap_data/` rather than treating them as committed project state. [Task 1]
- v1 citations as opaque search IDs plus vendor/Scribd/patent sources were rejected for v2; do not reuse that method. firecrawl_search/scrape ran out of credits (402/insufficient credits) and many publishers bot-wall urllib (IEA 403, MDPI 403, Springer JS-shell, IWA Cloudflare, OSTI timeout, ADB/ESMAP/ISO/USGBC 403/404); use a real browser instead. Direct PDF reads truncate at 60-80KB with PDF_NOREAD/startxref errors; download the full file (up to 15-60MB) and parse with fitz (PyMuPDF) with full-page scan. [Task 2][Task 3]
- Do not guess ISO numbers, LEED /v4/bdc paths, ADB slugs, or UNFCCC fashion URLs (retired/dead); use vbpl.vn plus congbao plus MAE plus browser instead. Move helpers with a `Get-ChildItem -Path scripts/* -Include` pattern (Move-Item multi-source positional fails); gitignore with `scratch/`; keep v1 untouched with deliverables uncommitted. [Task 4]
- Bash heredoc cat for large HTML failed with unexpected EOF; use the Write tool for HTML reports. The plan-template asset path may be missing; fall back to an existing plan file as format source. [Task 5]
- Full pytest collection fails on tests/test_units.py with ModuleNotFoundError: No module named 'pint' under system Python 3.14.2 with tools/.venv absent; rerun with --ignore=tests/test_units.py (118 passed) plus ceba/render/test_ee_deck.py separately (17 passed) instead of installing. PowerShell on this host rejects ls -la and pipe-to-cat; use Get-ChildItem / Get-Content. [Task 6]

# Task Group: F3 Three.js commercial render and master integration
scope: Improve and verify the F3 bedroom split viewer's rendered fidelity while keeping geometry valid, then determine actual branch integration state.
applies_to: cwd=C:\Users\tukum\Downloads\freecad-blender; reuse_rule=checkout-specific; rerun render verification and inspect branches/remotes before claiming completion or integration

## Task 1: Commercial-quality F3 viewer render, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T12-35-11-8SZI-f3_threejs_commercial_render_and_master_sync.md (cwd=C:\Users\tukum\Downloads\freecad-blender, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T19-35-19-01a0e2dc-b971-7780-9c28-d22d5914afda.jsonl, updated_at=2026-09-28T03:17:56+00:00, thread_id=01a0e2dc-b971-7780-9c28-d22d5914afda, model checks passed; full Chrome verification did not)

### keywords

- three.js, f3-split-viewer, commercial_pass.py, viewer_page_template.html, PBR, ACES, headless Chrome timeout, fd94c0f

## Task 2: Merge main/master, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T12-35-11-8SZI-f3_threejs_commercial_render_and_master_sync.md (cwd=C:\Users\tukum\Downloads\freecad-blender, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T19-35-19-01a0e2dc-b971-7780-9c28-d22d5914afda.jsonl, updated_at=2026-09-28T03:17:56+00:00, thread_id=01a0e2dc-b971-7780-9c28-d22d5914afda, master ahead locally; no push)

### keywords

- master, origin/master, git fetch origin, git rev-list, git push origin master, fd94c0f

## User preferences

- when the user asked for a render "till commercial quality" -> preserve the full visual-quality target and verify rendered output, not just geometry or model checks [Task 1]

## Reusable knowledge

- `commercial_pass.py` transforms `viewer_page_template.html` with sRGB/ACES, PBR materials, procedural wood/fabric textures, physical glass, warm studio lighting, shadow treatment, furniture edge lines, and closer camera. Generated viewer: `reports/2026-09-25-f3-bedroom-split/3d/f3-split-viewer.html`. [Task 1]
- `f3split_model.py --check` stayed 5/5 OK for options `0/A/B/C/D`, with 66/73/73/80/71 solids. Phone proof passed at `vw=390 vh=844 scrollW=390 cw=390 ch=844 bad=0`, including five 48x44 chips. [Task 1]
- The repository uses `master`, not `main`. After fetch, `master` was ahead one commit of `origin/master`, with zero incoming commits, so merge was a no-op. [Task 2]

## Failures and how to do differently

- Software-rendered headless Chrome timed out for some 1440px A/C shots. Use a focused probe and isolate expensive checks rather than blind polling; do not call verification green until a fresh full run passes. [Task 1]
- A local commit ahead of remote is not a completed integration. Confirm permission before `git push origin master`; do not assume "merge" authorizes a push. [Task 2]

# Task Group: Strict sequential shell-command reporting
scope: Execute explicitly listed shell commands one at a time and return only their results in the requested order.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp, cwd=C:\Users\tukum\tmp, and cwd=C:\Users\tukum\Downloads\remote\personal; reuse_rule=general output-mode preference, but command results and Git status are time-specific

## Task 1: Run sequential shell commands, success after an earlier output-format miss

### rollout_summary_files

- rollout_summaries/2026-09-27T22-56-42-rEvM-sequential_shell_commands_git_status.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-56-42-01a0e515-bd40-73e1-955a-d82b3379c41a.jsonl, updated_at=2026-09-27T22:57:05+00:00, thread_id=01a0e515-bd40-73e1-955a-d82b3379c41a, output-only request followed)
- rollout_summaries/2026-09-27T22-55-17-XvF4-sequential_shell_command_output.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-55-21-01a0e514-73df-7400-9bc7-043aa82f8676.jsonl, updated_at=2026-09-27T22:55:50+00:00, thread_id=01a0e514-73df-7400-9bc7-043aa82f8676, earlier response added commentary and omitted empty status)
- rollout_summaries/2026-09-27T22-49-27-zoH7-sequential_shell_command_reporting.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-49-29-01a0e50f-1b75-7513-82bd-d4e515a3fc39.jsonl, updated_at=2026-09-27T22:49:58+00:00, thread_id=01a0e50f-1b75-7513-82bd-d4e515a3fc39, output-only request followed)
- rollout_summaries/2026-09-27T22-39-55-9bZo-sequential_shell_command_output_only.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-39-57-01a0e506-60e9-7eb1-a6a0-09232ecf4a12.jsonl, updated_at=2026-09-27T22:40:29+00:00, thread_id=01a0e506-60e9-7eb1-a6a0-09232ecf4a12, commentary and empty-result miss)
- rollout_summaries/2026-09-27T22-34-08-2SDo-sequential_shell_command_check.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-34-08-01a0e501-136c-73b1-bc1a-4ceb5c84b8e2.jsonl, updated_at=2026-09-27T22:34:43+00:00, thread_id=01a0e501-136c-73b1-bc1a-4ceb5c84b8e2, output-only request followed)
- rollout_summaries/2026-09-27T22-19-28-xXGf-sequential_shell_command_reporting.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-19-28-01a0e4f3-a61a-7bc1-aa4b-3bb44d1b4f8f.jsonl, updated_at=2026-09-27T22:19:55+00:00, thread_id=01a0e4f3-a61a-7bc1-aa4b-3bb44d1b4f8f, commentary miss)
- rollout_summaries/2026-09-27T22-10-01-jrJs-run_shell_commands_and_report_output.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-10-01-01a0e4ea-ff26-7b50-bf71-b3018ef4b2f6.jsonl, updated_at=2026-09-27T22:10:34+00:00, thread_id=01a0e4ea-ff26-7b50-bf71-b3018ef4b2f6, output-only request followed)
- rollout_summaries/2026-09-27T22-05-42-LzOh-sequential_shell_command_output_reporting.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T05-05-45-01a0e4e7-0b59-7b20-a809-f9110ec48641.jsonl, updated_at=2026-09-27T22:08:05+00:00, thread_id=01a0e4e7-0b59-7b20-a809-f9110ec48641, repeated output-only request followed)

### keywords

- powershell, exec, git --version, git status --short, output-only, Nothing else, sequential-commands

## Task 2: Create a folder and execute a command sequence, success

### rollout_summary_files

- rollout_summaries/2026-09-27T21-08-56-FpBL-sequential_shell_commands_flashtest_tui.md (cwd=C:\Users\tukum\tmp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T04-08-56-01a0e4b3-14e9-7700-8744-c6e373f70a71.jsonl, updated_at=2026-09-27T21:09:31+00:00, thread_id=01a0e4b3-14e9-7700-8744-c6e373f70a71, requested folder/commands completed separately)

### keywords

- flashtest-tui, tui.txt, mkdir, dir, git --version, one at a time, Then reply done

## Task 3: Verify shell commands in remote personal workspace, success

### rollout_summary_files

- rollout_summaries/2026-09-29T13-55-27-Bv86-sequential_shell_command_verification.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\29\rollout-2026-09-29T20-55-28-01a0ed72-ef51-7223-9ac1-1440339d94ea.jsonl, updated_at=2026-09-29T13:56:04+00:00, thread_id=01a0ed72-ef51-7223-9ac1-1440339d94ea, four commands completed in order)

### keywords

- PowerShell, exec_command, guidance.md, echo check, git version 2.52.0.windows.1, git status --short, Nothing else

## User preferences

- when the user says "Run these shell commands one at a time and report output ... Nothing else." -> execute separately, suppress progress commentary, and return every result in order, including an empty `git status --short` result [Task 1]
- when the user says "run these shell commands one at a time inside it" and "Then reply done." -> use separate invocations in the requested directory, verify the requested artifact, then give only the requested acknowledgement [Task 2]

## Reusable knowledge

- Git was `2.52.0.windows.1` and `git status --short` was empty in this workspace at the time. [Task 1]
- In `C:\Users\tukum\tmp`, `mkdir flashtest-tui`, `echo tui > tui.txt`, `dir`, and `git --version` succeeded as separate executions; `dir` confirmed `tui.txt`. [Task 2]
- Git reported `2.52.0.windows.1` in the personal workspace. Recheck `git status --short` at execution time rather than retaining its file list as durable state. [Task 3]

## Failures and how to do differently

- Do not emit commentary before or between commands when the user says "Nothing else." Do not silently omit an empty command result. [Task 1]

# Task Group: Windows Codex remote-control, Herdr, and terminal diagnostics
scope: Start or diagnose local Codex/Herdr workflows on Windows while preserving requested CWD/focus behavior and isolating competing automation before global configuration changes.
applies_to: cwd=C:\Users\tukum and cwd=C:\Users\tukum\Downloads\freecad-blender; reuse_rule=machine-specific; daemon state, socket paths, and temporary config changes must be rechecked

## Task 1: Start Codex remote-control daemon, mixed

### rollout_summary_files

- rollout_summaries/2026-09-27T20-27-01-4Eme-start_codex_remote_control.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T03-27-01-01a0e48c-b517-7020-ba8d-14cb0aa28aa2.jsonl, updated_at=2026-09-27T20:38:32+00:00, thread_id=01a0e48c-b517-7020-ba8d-14cb0aa28aa2, connected daemon verified)
- rollout_summaries/2026-09-27T08-34-09-Mobb-codex_remote_control_elevated_windows_shell_failure.md (cwd=C:\Users\tukum\Downloads\freecad-blender, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T15-34-09-01a0e200-0df8-7a91-bcbe-0025b53d1e65.jsonl, updated_at=2026-09-27T12:38:35+00:00, thread_id=01a0e200-0df8-7a91-bcbe-0025b53d1e65, elevated shell blocked startup)

### keywords

- codex remote-control start --json, codex app-server daemon version, codex remote-control pair, app-server-control.sock, non-elevated terminal, Administrator, session 0

## Task 2: Launch Herdr Claude workspaces, clear AGENTS.md, and diagnose terminal flashes, success

### rollout_summary_files

- rollout_summaries/2026-09-27T09-15-21-9G7p-codex_remote_herdr_flash_investigation.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T16-15-21-01a0e225-c7ec-7312-b883-d0bd4f6768cb.jsonl, updated_at=2026-09-29T21:25:53+00:00, thread_id=01a0e225-c7ec-7312-b883-d0bd4f6768cb, Herdr launches succeeded; AGENTS.md emptied; flash root cause isolated to rom-hack loop)

### keywords

- herdr workspace create, herdr agent start, --no-focus, interactive_ready, AGENTS.md, codex remote-control start --json, chrome-devtools-axi, rom-hack, terminal-flash, procwatch, hooks.json, SessionStart, notify, --skip-git-repo-check

## Task 3: Launch Herdr workspaces on background default plus gateway, agy, remote-migration, and update ops, success

### rollout_summary_files

- rollout_summaries/2026-09-29T21-22-27-0X40-herdr_spaces_gateway_agy_remotes_update.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T04-22-27-01a0ef0c-2b53-7bd1-9b58-c0eb3a246b04.jsonl, updated_at=2026-10-06T12:46:31+00:00, thread_id=01a0ef0c-2b53-7bd1-9b58-c0eb3a246b04, city-ghg no-agent plus ceba/ee-heat/reopt-pysam/csim-copy/workflow-bench/baby-context/pacta-trisk launches; Hermes gateway restart; agy 1.2.16 install; 22 tah-allotrope remotes migrated to TukuCorp; Herdr 0.9.3 stable update; file-viewer keybinding debug; supersedes the deleted background-default-only version of the same thread)

### keywords

- herdr workspace create --no-focus, herdr agent start, herdr workspace focus, agent kind claude codex, unique agent names, Get-ChildItem -Filter, HERDR_ENV, herde typo, hermes gateway restart, agy install, git remote set-url TukuCorp, herdr update 0.9.3, file-viewer prefix ctrl+b

## Task 4: Launch baby-context and city-ghg spaces with Claude after cwd correction, success

### rollout_summary_files

- rollout_summaries/2026-10-06T13-01-43-OWsU-herdr_launch_baby_context_city_ghg_claude.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T20-01-43-01a1114e-4195-72d2-8166-6e9f05209aa8.jsonl, updated_at=2026-10-06T22:34:23+00:00, thread_id=01a1114e-4195-72d2-8166-6e9f05209aa8, baby-context first launched at wrong cwd then fixed to Downloads baby-context after user correction; city-ghg launched correctly)

### keywords

- herdr workspace create --no-focus, baby-context, city-ghg, Downloads cwd, HERDR_ENV re-check, agent name taken, baby-claude city-claude

## Task 5: Launch 5 background Claude workspaces with short-label convention, success

### rollout_summary_files

- rollout_summaries/2026-10-06T22-02-44-S5V5-herdr_launch_claude_workspaces_batch.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\07\rollout-2026-10-07T05-02-44-01a1133d-9248-7f42-92dd-3038cc380fa7.jsonl, updated_at=2026-10-07T09:05:42+00:00, thread_id=01a1133d-9248-7f42-92dd-3038cc380fa7, city-ghg pdd-auto ee-heat copper cpi each with idle Claude agent)

### keywords

- herdr workspace create --no-focus, herdr agent start, city-ghg-claude, pdd-auto, ee-heat, copper, cpi, short label, remote slash path

## User preferences

- when the user issues `codex remote-control start` -> execute directly and report the concrete startup/verification result without unrelated repository exploration [Task 1]
- when launching requested Herdr spaces, preserve the requested CWD, use Claude, and avoid stealing focus unless asked [Task 2]
- when the user reports "still crazy flashes" and asks to "monitor more to be sure" -> gather live comparative process evidence rather than speculate [Task 2]
- when the user says "Delete global current agents.md for codex as I want to work on a new one" then "Both" -> empty both C:\Users\tukum\AGENTS.md and C:\Users\tukum\.codex\AGENTS.md to a clean slate via apply_patch when Remove-Item is policy-blocked, then ask for the new stack [Task 2]
- when the user says "fix temp", "try al", or "monitor more to be sure" during flash diagnosis -> apply reversible TEMP-FLASH-TEST disables and re-trace the identical minimal task to compare spawn counts [Task 2]
- when a new workspace stayed in the background and the user asked "Why no focus, just a normal one", then corrected "Never mind still use herdr default for future" -> create Herdr workspaces with `--no-focus` (background default) unless the user explicitly asks for focus; use `herdr workspace focus <id>` only for an immediate one-off request [Task 3]
- when the user says "Launch herdr space at <project> no agent" -> create the workspace only and do not start an agent [Task 3]
- when the user types "herde" for a Herdr launch -> treat it as herdr without interrupting for clarification [Task 3]
- when launching a Herdr space for a named project, the user corrected: "baby-context folder exist dud" -> search C:\Users\tukum\Downloads (including -Recurse -Depth 3) before claiming a folder is missing; project dirs live under Downloads, never directly under C:\Users\tukum [Task 4]
- when the user says "launch herdr space at remote/<name> with claude agent" -> label the workspace <name> (not remote/<name>), cwd C:\Users\tukum\Downloads\remote\<name>, agent <name>-claude [Task 5]

## Reusable knowledge

- Use `codex remote-control start --json` for machine-readable health; then verify with `codex app-server daemon version` and, if pairing is needed, `codex remote-control pair`. A prior connected daemon reported `status: connected`, `daemon.status: alreadyRunning`, and a control socket under `C:\Users\tukum\.codex\app-server-control\`. [Task 1]
- Create Herdr workspaces with `--no-focus`, then parse workspace/pane IDs from JSON before `herdr agent start ... --kind claude --pane <id>`; confirm `interactive_ready` rather than predicting IDs. [Task 2]
- The decisive flash evidence was user confirmation that flashes stopped when the rom-hack session stopped. Its repeated `chrome-devtools-axi` eval/wait/screenshot processes were the primary cause; the Codex startup burst (about 14 helpers down to 3 after disabling firecrawl/notebooklm/officecli and SessionStart hooks) was secondary. Pause parallel automation before attributing flashes to Codex. [Task 2]
- `codex remote-control start --json` exiting 0 with status connected plus socket C:\Users\tukum\.codex\app-server-control\app-server-control.sock present is itself the verification; `codex agents` needs an interactive TUI and fails non-interactively. `codex exec` in C:\Users\tukum needs --skip-git-repo-check; trace with a minimal read-only hello task. [Task 2]
- In Windows PowerShell 5.1 `Get-ChildItem -MaxDepth 1` is unsupported; list without it. [Task 2]
- Launch sequence: verify the target dir exists, read the Herdr skill at `C:\Users\tukum\.agents\skills\herdr\SKILL.md`, then `herdr workspace create --cwd "<path>" --label "<label>" --no-focus` and parse the returned workspace/tab/root-pane IDs before `herdr agent start <name> --kind <claude|codex> --pane <pane-id>`; agent starts took about 4-5s (allow yield up to 55s) and report `interactive_ready`. Launched w3C city-ghg (no agent), w3D ceba (claude), w3E ee-heat (codex), w3K reopt-pysam (claude). [Task 3]
- Launch sequence: verify the target dir exists, read the Herdr skill at `C:\Users\tukum\.agents\skills\herdr\SKILL.md`, then `herdr workspace create --cwd "<path>" --label "<label>" --no-focus` and parse the returned workspace/tab/root-pane IDs before `herdr agent start <name> --kind <claude|codex> --pane <pane-id>`; agent starts took about 4-5s (allow yield up to 55s) and report `interactive_ready`. Launched w3C city-ghg (no agent), w3D ceba (claude), w3E ee-heat (codex), w3K reopt-pysam (claude), w3M csim-copy (claude), w3N workflow-bench (claude); names map under C:\Users\tukum\Downloads except remote/ceba. [Task 3]
- Agent names must be unique and match `[a-z][a-z0-9_-]{0,31}`; the start command needs an existing shell pane. When the project path is ambiguous, `Get-ChildItem -Directory "C:\Users\tukum\Downloads" -Recurse -Depth 3 -Filter "*<name>*"` locates it. [Task 3]
- Workspaces evaporate between sessions; always run `herdr workspace list` plus `herdr agent list` before creating, and recreate fresh when a space is gone. When a plain agent name is taken, use `<label>-claude` or `<label>-2`. [Task 3][Task 4][Task 5]
- Hermes gateway down signature: `herdr agent get hermes` returns `agent_not_found`, `hermes gateway status` prints empty, heartbeat file stale; fix with `hermes gateway restart` (~60s boot) then verify fresh heartbeat plus `logs/gateway.log` showing control pipe and discord/api_server connected. Empty status output means dead, not healthy. [Task 3]
- agy CLI installs from `https://antigravity.google/cli/install.cmd` (not npm); binary lands at `%LOCALAPPDATA%\agy\bin\agy.exe`; refresh PATH in the current session; Herdr already accepts `--kind agy`. [Task 3]
- Bulk org migration preserves https-vs-ssh and swaps case-insensitively `(?i)tah-allotrope` to `TukuCorp` via `git remote set-url`; re-sweep until leftover count is 0. [Task 3]
- Herdr refuses self-update inside an attached session; clear `HERDR_ENV/HERDR_WORKSPACE_ID/HERDR_TAB_ID/HERDR_PANE_ID` in the same command, then `herdr update --handoff` installs stable (0.9.3). [Task 3]
- herdr-file-viewer default prefix is `ctrl+b` (press, release, then `f`); when keys do nothing but `herdr plugin action invoke open-file-viewer-windows` succeeds, the failure is key delivery, not the plugin. [Task 3]
- Related skill: skills/herdr-workspace-launch/SKILL.md

## Failures and how to do differently

- Windows rejects remote-control startup from an elevated session: `start the Windows daemon from a non-elevated terminal; shared clients must not inherit administrator privileges`. Do not try `runas` or cross-session scheduled-task workarounds; have the user use a normal interactive PowerShell, then verify. [Task 1]
- Split PowerShell/tool calls when quoting yields `SyntaxError: Invalid or unexpected token`. In PowerShell, use `rg` or `Get-ChildItem -Recurse | Select-String`; `Select-String -Recurse` is invalid. [Task 1]
- Before disabling global Codex `notify`, MCP servers, or SessionStart hooks, pause unrelated automation and compare a clean baseline. Earlier temporary config/hook changes remained active and need deliberate review/restoration. Emptying `AGENTS.md` is not deletion. [Task 2]
- `Remove-Item` for AGENTS.md was blocked by policy via exec_command; empty files section-by-section with apply_patch and verify with Get-Item Length instead of retrying deletes. hooks.json allows no comments; an uncommented placeholder breaks JSON, so rewrite to valid `"SessionStart": []`. [Task 2]
- Bash `test "${HERDR_ENV:-}" = 1` is not recognized in PowerShell; check `$env:HERDR_ENV` instead. [Task 3]
- A first-attempt HERDR_ENV empty refusal can be transient; re-check `$env:HERDR_ENV` with PowerShell syntax before final refusal. [Task 4]


# Task Group: pacta-trisk docs-only git commit-push after slow-R abort
scope: Commit and push a docs-only change in pacta-trisk when the full R suite is too slow for the request; leave unrelated untracked work alone.
applies_to: cwd=C:\Users\tukum\Downloads\pacta-trisk; reuse_rule=checkout-specific (R 4.5.2 suite, VND golden numbers); docs-only reasoning transfers to other R-gated repos

## Task 1: Cancel slow R verification then push docs-only 168bb27, success

### rollout_summary_files

- rollout_summaries/2026-10-06T08-17-49-gzA8-git_commit_push_main_lessons_docs_only.md (cwd=C:\Users\tukum\Downloads\pacta-trisk, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T15-17-50-01a1104a-5649-7032-8471-380e8b645fac.jsonl, updated_at=2026-10-06T12:23:51+00:00, thread_id=01a1104a-5649-7032-8471-380e8b645fac, first attempt cancelled during slow R suite with tree untouched; retry committed only lessons.md as 168bb27 and pushed)

### keywords

- git commit push main, lessons.md, 168bb27, pytest dashboard, run_tests.R, taskkill Rscript, untracked gtb, TukuCorp remote notice

## User preferences

- when a git request triggers a long silent verification, the user interrupted: "what were we doing here, i tot this was about git" -> for docs-only commits use git diff --stat plus the fast suite, state the slow-suite skip reason upfront, and never hold the request on a full run without explanation [Task 1]
- when the user says "cancel all" -> kill background work and confirm the tree is untouched via status/log [Task 1]
- when the user repeats git commit push main with no extra spec -> keep the prior agreed scope (tracked lessons.md only) and leave untracked gtb plus stray reports for explicit opt-in [Task 1]

## Reusable knowledge

- Docs-only 12-line lessons.md change does not affect R golden numbers or byte-identity; python -m pytest dashboard/tests (79 passed) is sufficient evidence. [Task 1]
- Untracked gtb client folder and reports/Wave5_Implementation_Report.html stay uncommitted by default; commit message used was a generated scope summary about look and tone, not content. [Task 1]
- Push printed a repo-moved notice toward https://github.com/TukuCorp/pacta-trisk.git; suggest updating git remote set-url origin later. [Task 1]

## Failures and how to do differently

- Full tools/run_tests.R via quoted Rscript path runs many minutes with pre-existing test_coverage_report.R failures unrelated to docs changes; do not gate docs-only commits on it. [Task 1]

# Task Group: Windows laptop cleanup and firstmate uninstall
scope: Fully remove a repo-distributed tool footprint (checkout, generated homes, config refs) on this Windows laptop after confirming no registered app entry, leaving a manual-delete snippet when deletion is policy-blocked.
applies_to: cwd=C:\Users\tukum; reuse_rule=machine-specific; recheck running processes and config refs before deleting anything

## Task 1: Uninstall firstmate by kunchen, partial

### rollout_summary_files

- rollout_summaries/2026-10-01T05-53-27-K5z3-uninstall_firstmate_kunchen_laptop.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\01\rollout-2026-10-01T12-53-28-01a0f606-5e2c-7710-abb5-a82541d450c1.jsonl, updated_at=2026-10-01T06:07:53+00:00, thread_id=01a0f606-5e2c-7710-abb5-a82541d450c1, no registered app; .claude.json refs pruned; repo folders left for manual delete)

### keywords

- firstmate, kunchen, kunchenguid, uninstall, fm-homes, .claude.json, githubRepoPaths, treehouse, herdr, Remove-Item blocked by policy

## User preferences

- when asked to uninstall, the user said "uninstall firstmate by kunchen from this laptop" -> they expect full footprint removal including repo checkout, generated homes, and config refs, not just a Programs/winget entry [Task 1]

## Reusable knowledge

- firstmate (github.com/kunchenguid/firstmate) is not a Windows installer app; its README states the cloned repo is the distro, so absence in Win32_Product / Get-Package / winget list / Uninstall registry / AppxPackage / services / scheduled tasks / PATH is expected. Full footprint on this machine was C:\Users\tukum\firstmate (about 100 MB repo checkout), C:\Users\tukum\fm-homes (hermes, omp, opencode), C:\Users\tukum\.claude\projects\C--Users-tukum-firstmate, and C:\Users\tukum\.omp\agent\sessions\-firstmate, plus .claude.json refs. [Task 1]
- .claude.json stores firstmate in two places: projects["C:/Users/tukum/firstmate"] and githubRepoPaths["kunchenguid/firstmate"]; both must be removed (backup made at C:\Users\tukum\.claude.json.bak-firstmate-uninstall). Do not delete C:\Users\tukum\.local\bin\treehouse.exe as firstmate cleanup (its installer script is CI-only for Linux/macOS) and do not kill herdr processes/workspaces as firstmate crew. [Task 1]
- Manual finish command: Remove-Item -LiteralPath 'C:\Users\tukum\firstmate' -Recurse -Force; Remove-Item -LiteralPath 'C:\Users\tukum\fm-homes' -Recurse -Force; plus -ErrorAction SilentlyContinue removes for the .claude projects and .omp session paths. Verification is Select-String .claude.json for firstmate|kunchenguid returning zero plus Test-Path checks. [Task 1]

## Failures and how to do differently

- Remove-Item for the firstmate folders was blocked by policy (exec_command CreateProcess Rejected at powershell.exe launch); verify deletion ability early and hand the user the exact PowerShell snippet instead of retrying bulk deletes. Splitting verification (Test-Path) from deletion still hit blocks, so provide the manual command. [Task 1]
- Avoid Win32_Product and broad C:\Users\tukum Recurse Depth 4 scans (slow or EXIT:undefined); prefer targeted registry Uninstall keys, winget list --name, Get-AppxPackage, Get-Process, Test-Path, and FM_HOME env checks. [Task 1]

# Task Group: ShortcutXL BYOM with OpenCode Go
scope: Install and configure ShortcutXL on this Windows machine with OpenCode Go as a custom OpenAI-compatible provider, then set and verify the default model.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=safe for the user's local ShortcutXL and OpenCode Go setup, but recheck CLI version, model inventory, environment-variable name, and provider requirements before changing configuration

## Task 1: Install ShortcutXL, configure OpenCode Go, and change the default model, success

### rollout_summary_files

- rollout_summaries/2026-09-22T03-02-09-V4k5-shortcutxl_opencode_go_byom_setup.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\22\rollout-2026-09-22T10-02-10-01a0c710-4f20-7003-ad8e-2de36ee729f5.jsonl, updated_at=2026-09-22T03:38:09+00:00, thread_id=01a0c710-4f20-7003-ad8e-2de36ee729f5, live provider request and default-model change verified)

### keywords

- shortcutxl, shortcut CLI, BYOM, OpenCode Go, openai-completions, x-opencode-session, MissingSessionID, models.json, settings.json, muse-spark-1.3-contributor

## User preferences

- when the user said "install shortcut cli then setup byok using opencode go api key for me" -> execute directly, give concise progress updates, and verify the complete configuration with a live request [Task 1]
- when the user said "change default shortcut model to muse spark 1.3 contributor" -> make the change and report the exact resulting provider/model pair [Task 1]

## Reusable knowledge

- `shortcutxl` 0.3.91 installs globally with executable `shortcut`. Custom providers live in `C:\Users\tukum\.shortcut\agent\models.json`; global defaults live in `C:\Users\tukum\.shortcut\agent\settings.json`. [Task 1]
- ShortcutXL accepts `api: "openai-completions"`, `baseUrl`, an environment-variable name in `apiKey`, `models`, and `authHeader`. The OpenCode Go endpoint used was `https://opencode.ai/zen/go/v1`. Keep the key value out of memory and output. [Task 1]
- Allow `opencode.ai` and `*.opencode.ai` in the Shortcut sandbox. OpenCode Go Chat Completions needs an `x-opencode-session` header. [Task 1]
- Use `shortcut --assume-installed --list-models opencode-go` for a fast model-discovery check after installation. A live prompt through `kimi-k3` succeeded. The verified final default was `opencode-go/muse-spark-1.3-contributor`. [Task 1]
- Kimi Work did not document a BYOK or external-provider slot. OpenCode Go works inside OpenCode and supported agents, while Kimi models can be used through OpenCode Go. [Task 1]

## Failures and how to do differently

- Symptom: `Unexpected token '﻿'` when Shortcut reads JSON. Cause: a PowerShell JSON write added a UTF-8 BOM. Fix: write JSON with `[System.Text.UTF8Encoding]::new($false)`. [Task 1]
- Symptom: Go responds `MissingSessionID` or Shortcut reports `The model provider rejected the request`. Cause: the provider lacks the required session header or explicit auth handling. Fix: configure `x-opencode-session`, retain environment-variable based auth, then rerun model listing and a live prompt. [Task 1]
- Symptom: `Start-Process npm` fails because it resolves to `npm.ps1`, or `env` is unknown. Fix: use `cmd.exe /c npm ...` and PowerShell environment access such as `Get-ChildItem Env:`. [Task 1]
- Symptom: Shortcut first-run setup is slow. Fix: after installation, use `--assume-installed` for configuration checks and smoke tests. [Task 1]

# Task Group: OpenCode Go, ChatGPT extension, and Codex integration
scope: Troubleshoot OpenCode Go credentials in the ChatGPT browser extension and answer capability questions about Office model selection and Codex CLI/Desktop history.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=safe for Windows process-environment troubleshooting and local Codex/OpenCode integration questions, but treat extension paths, installed Office tooling, and desktop synchronization as time-specific

## Task 1: Fix `Missing environment variable: OPENCODE_GO_API_KEY`, success

### rollout_summary_files

- rollout_summaries/2026-09-15T22-53-24-SNNT-opencode_go_chatgpt_extension_and_codex_cli_history.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T05-53-24-01a0a746-68d2-7560-9d09-933f473cd129.jsonl, updated_at=2026-09-16T00:26:07+00:00, thread_id=01a0a746-68d2-7560-9d09-933f473cd129, user confirmed the browser restart fixed the extension)

### keywords

- Missing environment variable: OPENCODE_GO_API_KEY, Chrome extension, stale environment, opencode auth list, OpenCode Go api, PowerShell

## Task 2: Check custom model support in Excel and PowerPoint, success

### rollout_summary_files

- rollout_summaries/2026-09-15T22-53-24-SNNT-opencode_go_chatgpt_extension_and_codex_cli_history.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T05-53-24-01a0a746-68d2-7560-9d09-933f473cd129.jsonl, updated_at=2026-09-16T00:26:07+00:00, thread_id=01a0a746-68d2-7560-9d09-933f473cd129, no built-in custom model picker found)

### keywords

- Excel live control, PowerPoint, custom OpenCode Go model, ChatGPT add-in, Codex Presentations workflow, OPENCODE_GO_API_KEY

## Task 3: Determine whether Codex CLI projects appear in the desktop list, uncertain

### rollout_summary_files

- rollout_summaries/2026-09-15T22-53-24-SNNT-opencode_go_chatgpt_extension_and_codex_cli_history.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T05-53-24-01a0a746-68d2-7560-9d09-933f473cd129.jsonl, updated_at=2026-09-16T00:26:07+00:00, thread_id=01a0a746-68d2-7560-9d09-933f473cd129, local history confirmed but desktop-list synchronization unverified)

### keywords

- Codex CLI, desktop history, rollout-*.jsonl, codex agents --help, codex resume --all, TERM is set to "dumb", unsupported call

## User preferences

- when the user asked to "investigate and fix" the missing-variable error and confirmed "ok working now" -> prioritize direct diagnosis, a practical fix, and concise confirmation [Task 1]
- when the user asked about a custom/OpenCode Go model for Office -> distinguish model selection from document-tool routing before proposing a workflow [Task 2]

## Reusable knowledge

- Windows processes inherit their environment at launch. If Chrome and its extension host started before `OPENCODE_GO_API_KEY` was refreshed, verify the variable and credential presence without printing them, then ask for a full Chrome exit and relaunch. Prefer a guided restart over force-killing Chrome because the user has multiple profiles. [Task 1]
- There was no built-in custom model picker for Excel or PowerPoint. Excel live control uses the ChatGPT add-in and connected-document tools. PowerPoint uses the Codex Presentations workflow. `OPENCODE_GO_API_KEY` is for OpenCode CLI/API or provider plugins, not Office add-ins. A split workflow can reason with OpenCode Go then create or edit `.xlsx` or `.pptx` through Codex tooling. [Task 2]
- Local CLI sessions exist under `C:\Users\tukum\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`. This does not prove they populate the Codex desktop thread list. [Task 3]

## Failures and how to do differently

- Do not print credentials. Compare presence, length, or a short prefix only. [Task 1]
- PowerShell does not support Unix `ls -la` or `head`. Use `Get-ChildItem`, `Get-Content`, and `Select-Object -First`. [Task 1]
- Do not claim CLI/Desktop history sharing is confirmed. `mcp__codex_app.list_threads` was unsupported and `codex resume --all` refused to start with `TERM` set to `dumb`. Use a supported app-server interface, a non-interactive route, or a proper TTY to test it. [Task 3]

# Task Group: Official EVA Air fare lookup with Browser Control
scope: Retrieve official EVA Air fares and screenshots using Browser Control, with strict evidence requirements for live price results.
applies_to: cwd=C:\Users\tukum\Downloads\city-ghg; reuse_rule=safe for similar browser-control fare research, but treat routes, page state, captcha behavior, and saved screenshots as run-specific

## Task 1: Check official EVA Air prices and capture screenshots, failed

### rollout_summary_files

- rollout_summaries/2026-09-17T10-08-36-Zdst-eva_air_fare_lookup_failed.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\17\rollout-2026-09-17T17-08-36-01a0aed6-ed58-7f13-a1f2-e7151fb20961.jsonl, updated_at=2026-09-17T10:33:45+00:00, thread_id=01a0aed6-ed58-7f13-a1f2-e7151fb20961, booking flow stalled and no fare was verified)

### keywords

- EVA Air, browser-control, booking-multi.aspx, browser-control session new eva1, Session not found, nffValidator, captcha, page.$$eval, fare search, screenshot price

## User preferences

- when the user asked to "check the price on official website" and "screenshot price" -> return screenshots containing the actual fare result, not homepage or booking-progress screenshots [Task 1]

## Reusable knowledge

- The official booking URL reached was `https://booking.evaair.com/flyeva/EVA/B2C/booking-multi.aspx?lang=en-us`. Browser Control requires an explicit session, for example `browser-control session new eva1`, before commands use `--session eva1`. [Task 1]
- `eva-home.png` and `eva-progress7.png` through `eva-progress9.png` prove page state only. They do not prove any fare price. [Task 1]

## Failures and how to do differently

- No fare results were produced for BR17, BR385, or the requested multi-stop return. Do not claim prices were found. [Task 1]
- Symptom: `Session not found: eva1`. Cause: commands ran against an unknown session. Fix: create the named session before use. [Task 1]
- Symptom: Browser Control rejects `60000.0` or process/session IDs such as `73373.0`. Cause: serialized floats where the tool needs integers. Fix: pass integer values. [Task 1]
- Symptom: `TypeError: page.eval is not a function` from `page.$$eval`. Cause: the installed Browser Control runtime does not expose standard Playwright APIs. Fix: use documented Browser Control APIs only. [Task 1]
- Symptom: closing the booking modal raises `ReferenceError: nffValidator is not defined` and the flow stays before results or captcha completion. Fix: treat the page as stuck, pivot, or report the inability. [Task 1]

# Task Group: Local folder boundaries and account identity
scope: Respect non-invasive folder questions and distinguish Windows account information from ChatGPT account identity.
applies_to: cwd=C:\Users\tukum\Downloads\city-ghg; reuse_rule=safe for similar local-environment questions on this machine, but re-verify identity output and never infer project contents or cloud identity from a path

## Task 1: Describe a folder without inspection, success

### rollout_summary_files

- rollout_summaries/2026-09-16T01-42-36-Puhz-non_invasive_folder_and_account_identification.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T08-42-36-01a0a7e1-5141-7fe1-a517-419911772751.jsonl, updated_at=2026-09-17T00:47:13+00:00, thread_id=01a0a7e1-5141-7fe1-a517-419911772751, no filesystem inspection performed)

### keywords

- tell me about the folder without doing anything, non-invasive inspection, C:\Users\tukum\Downloads\city-ghg, city-ghg

## Task 2: Identify the local or ChatGPT account, partial

### rollout_summary_files

- rollout_summaries/2026-09-16T01-42-36-Puhz-non_invasive_folder_and_account_identification.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T08-42-36-01a0a7e1-5141-7fe1-a517-419911772751.jsonl, updated_at=2026-09-17T00:47:13+00:00, thread_id=01a0a7e1-5141-7fe1-a517-419911772751, Windows account identified; ChatGPT email inaccessible from CLI)

### keywords

- whoami, whoami /upn, ChatGPT account, Windows local account, Select-Object -First, unsupported call

## User preferences

- when the user said "tell me about the folder without doing anything" -> do not list, read, search, or modify files. Explain only what the path itself supports. [Task 1]

## Reusable knowledge

- The `city-ghg` name suggests a city greenhouse-gas project, but that was not verified because contents were not inspected. [Task 1]
- `whoami` identifies the current Windows account. It does not identify the signed-in ChatGPT account. When the user means ChatGPT, direct them to the profile avatar or Settings → Account/Profile. [Task 2]

## Failures and how to do differently

- `whoami /upn` can report that the user is not a domain user. State that result without inferring a cloud or ChatGPT identity. [Task 2]
- If GitHub identity tooling returns `unsupported call`, report the limitation. Do not guess the identity. [Task 2]
- Use `Select-Object -First` instead of Unix `head` in PowerShell. [Task 2]

# Task Group: Selected Chrome tab inspection when browser tools are unavailable
scope: Answer requests to inspect a selected browser tab only when a browser tool can expose page state; otherwise obtain user-provided evidence.
applies_to: cwd=C:\Users\tukum\Documents\Codex\2026-09-16\mon; reuse_rule=safe for browser-inspection failure handling across checkouts, but tab IDs and URLs are run-specific

## Task 1: Inspect the Eufy camera page, failed

### rollout_summary_files

- rollout_summaries/2026-09-16T13-42-24-8YKf-browser_page_inspection_tool_unavailable.md (cwd=C:\Users\tukum\Documents\Codex\2026-09-16\mon, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T20-42-24-01a0aa74-4f9e-7ff3-ae86-6464493a9513.jsonl, updated_at=2026-09-16T13:43:01+00:00, thread_id=01a0aa74-4f9e-7ff3-ae86-6464493a9513, neither available inspection method worked)

### keywords

- Eufy, mysecurity.eufylife.com, chrome_extension.getTabContext, mcp__cua_repl.js, await cua.getState(), unsupported call

## Reusable knowledge

- The selected page was `https://mysecurity.eufylife.com/#/camera`, but no contents were visible or verifiable when both `chrome_extension.getTabContext` and `mcp__cua_repl.js` returned `unsupported call`. [Task 1]

## Failures and how to do differently

- Verify browser-tool availability first. If the tool is unsupported, state the limitation immediately and request a screenshot, pasted text, or user description. Do not infer page contents. [Task 1]

# Task Group: Codex CLI sign-in and ChatGPT subscription verification
scope: Check local Codex CLI sign-in safely and state the limit of subscription-plan evidence available from local auth and blocked endpoints.
applies_to: cwd=C:\Users\tukum; reuse_rule=safe for local Codex CLI authentication checks, but treat sign-in state and subscription status as current-session facts that must be rechecked

## Task 1: Verify Codex sign-in and account switching, success

### rollout_summary_files

- rollout_summaries/2026-09-15T22-36-38-WGj0-codex_login_account_plan_check.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T05-36-38-01a0a737-0ff1-7031-8020-3568061e37d2.jsonl, updated_at=2026-09-15T22:38:58+00:00, thread_id=01a0a737-0ff1-7031-8020-3568061e37d2, sign-in verified without exposing auth data)

### keywords

- codex login status, Logged in using ChatGPT, codex login, codex logout, --device-auth, --with-api-key, auth.json

## Task 2: Determine whether the ChatGPT account is free or paid, uncertain

### rollout_summary_files

- rollout_summaries/2026-09-15T22-36-38-WGj0-codex_login_account_plan_check.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\16\rollout-2026-09-16T05-36-38-01a0a737-0ff1-7031-8020-3568061e37d2.jsonl, updated_at=2026-09-15T22:38:58+00:00, thread_id=01a0a737-0ff1-7031-8020-3568061e37d2, local and direct HTTP checks were inconclusive)

### keywords

- subscription, My plan, HTTP 403, api.openai.com/v1/models, chatgpt.com/backend-api/subscriptions, ChatGPT authentication

## Reusable knowledge

- `codex login status` returned `Logged in using ChatGPT`. Use `codex login` for browser authentication. Use `codex logout` then `codex login` to switch accounts. `--device-auth` and `--with-api-key` are alternatives. [Task 1]
- `C:\Users\tukum\.codex\auth.json` contains sensitive auth data. Do not print its contents or persist account identifiers, JWTs, token values, token prefixes, refresh tokens, access tokens, or account IDs. [Task 1]
- Local identity claims did not include a subscription claim. Direct account and subscription endpoint checks returned HTTP 403, so the reliable plan check is ChatGPT Settings → Subscription / My plan while signed in. [Task 2]

## Failures and how to do differently

- Do not infer a paid plan because Codex works. Report it as unknown unless the official subscription page confirms it. [Task 2]
- In PowerShell, use `Select-Object -First` rather than Unix `head`. [Task 1]

# Task Group: Anthropic threat-report Vietnam review and GTG case analysis
scope: Inspect the complete Anthropic threat-report PDF for Vietnam references and explain named GTG cases with source-bounded attribution.
applies_to: cwd=C:\Users\tukum\Downloads\remote\personal; reuse_rule=report-version-specific; download and search the exact PDF before making country or case claims

## Task 1: Check the full September 2026 report for Vietnam references, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-MWRQ-anthropic_report_vietnam_and_notable_cases.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b9f4-7df2-bb2c-502a3d775ec2.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b9f4-7df2-bb2c-502a3d775ec2, full-PDF search completed)

### keywords

- Anthropic, September 2026, Vietnam, Ho Chi Minh City, Southeast Asia, GTG-20006, GTG-10007, pdftotext, maxContentLength size of 10485760 exceeded

## Task 2: Inventory selected GTG cases and government-data exposure, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-MWRQ-anthropic_report_vietnam_and_notable_cases.md (cwd=C:\Users\tukum\Downloads\remote\personal, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b9f4-7df2-bb2c-502a3d775ec2.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b9f4-7df2-bb2c-502a3d775ec2, case inventory and selected explanations)

### keywords

- GTG-10007, Hunan, Changsha, DeepSeek, GTG-16001, GTG-15001, GTG-84005, GTG-50020, AI personas, Malaysian election

## User preferences

- when the webpage review found nothing, the user asked "What abt the full report?" -> locate and inspect the downloadable document rather than treating the webpage as complete [Task 1]
- when the user asked for "full detail," "complete inventory," and more cases -> provide case-by-case context, technical workflow, scale, victims, and response rather than a keyword-only summary [Task 1][Task 2]

## Reusable knowledge

- WebFetch failed with `maxContentLength size of 10485760 exceeded`. Direct download, `pdftotext -layout`, and local context search worked. [Task 1]
- The literal `Vietnam` was absent. The only named Vietnam-related text was the redacted `Ho Chi Minh City site $[]M` capex example in the DeepSeek/PRC-lab distillation section. GTG-20006 and GTG-10007 refer only to unnamed Southeast Asian entities, not Vietnam. [Task 1]
- GTG-10007 involved Chinese-speaking operators likely in Changsha/Hunan, including two students. It used Claude for exploit research, reconnaissance, malware, and campaign coordination, targeted roughly 50 organizations, and retrieved records from an unnamed Southeast Asian government agency. [Task 2]
- GTG-16001 describes DeepSeek relaying some third-party-harness requests to Claude, exposing examples that included Russian government-database credentials and PRC police-record work. Selected unusual cases include GTG-15001 dating scams, GTG-84005 Malaysian election manipulation, and GTG-50020 AI-vendor prompt-injection attacks. [Task 2]

## Failures and how to do differently

- A webpage-only pass missed the concrete Ho Chi Minh City reference and many GTG cases. Start with the full PDF when available, then distinguish named facts from geographic inference. [Task 1]

# Task Group: PDD-auto ranked grounding and registered reconciliation planning
scope: Plan verified improvements to PDD retrieval, methodology indexing, calculation validation, and Inegol registered-workbook reconciliation.
applies_to: cwd=C:\Users\tukum\Downloads\pdd-auto; reuse_rule=checkout-specific; re-run tests and inspect current configs/workbooks before implementation

## Task 1: Close walkthrough plan and create ranked-grounding reconciliation plan, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-jGrX-ranked_grounding_registered_reconciliation_plan.md (cwd=C:\Users\tukum\Downloads\pdd-auto, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-bb0b-7d43-9659-c609e5458615.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-bb0b-7d43-9659-c609e5458615, plan saved; no commit requested)

### keywords

- pdd-auto, ranked-grounding, BM25, methodology-index, Inegol, ACM0022, reconciliation, climate-zone, duplicate-yaml, test-isolation, plans/2026-09-11-ranked-grounding-and-registered-reconciliation-plan.md

## User preferences

- when the user required unattended execution, no questions or pickers, and an exact completion line -> make binding assumptions from repository evidence, document them in the plan, and finish with the requested marker [Task 1]
- when the user required the plan in project-root `plans/` and `PLAN_SAVED: plans/<filename>.md` -> preserve the exact location and confirmation format [Task 1]

## Reusable knowledge

- The implementation plan is `plans/2026-09-11-ranked-grounding-and-registered-reconciliation-plan.md`. Its six phases cover hygiene, methodology indexing, ranked grounding/self-exclusion, calculation/YAML validation, Inegol workbook reconciliation, and `pdd-agent reconcile`. [Task 1]
- Use `PYTHONPATH= uv run --no-sync ...` on this Windows checkout. The non-corpus suite then reported 974 passed, 7 deselected, 2 xfailed. [Task 1]
- `get_examples_for_section()` returned score `0.0` and effectively alphabetic/document-order examples; Inegol's own PDD could enter grounding. Collapsed text/plain methodology pages such as ACM0022 were skipped by TOC detection. [Task 1]
- `configs/demo/inegol_project_input.yaml` has duplicate `biomethanization_suitable_fraction` keys, so YAML silently uses the later `0.45`; the plan records workbook-derived `0.4312` as the binding replacement. [Task 1]

## Failures and how to do differently

- Reassert `C:\Users\tukum\Downloads\pdd-auto` or use absolute paths after skill/tool calls. Context changes caused misleading file-not-found errors. [Task 1]
- Preserve unrelated working-tree changes. The walkthrough triage committed only its target plan because another plan had pre-existing edits. [Task 1]
- Treat blocked-export normal return, Windows `pdd-agent --help` `UnicodeEncodeError`, and tests writing into `data/runs` as implementation gaps, not cosmetic observations. [Task 1]

# Task Group: PDD-auto portable package validation and CarbonCure review
scope: Validate, author, and summarize portable PDD field tests without overstating workflow or source-integrity results.
applies_to: cwd=C:\Users\tukum\Downloads\pdd-auto; reuse_rule=checkout-specific; re-run hashes, validators, and artifact QA for every package

## Task 1: CarbonCure VCS 4019 portable PDD demo, partial

### rollout_summary_files

- rollout_summaries/2026-09-21T13-48-49-wtp9-carboncure_portable_pdd_demo_run.md (cwd=C:\Users\tukum\Downloads\pdd-auto, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\21\rollout-2026-09-21T20-48-49-01a0c439-fa06-7d10-b226-02d81ca51a8b.jsonl, updated_at=2026-09-27T05:51:15+00:00, thread_id=01a0c439-fa06-7d10-b226-02d81ca51a8b, REVIEW_REQUIRED)

### keywords

- CarbonCure, VCS 4019, VM0043 v1.0, check_authored_pdd.py, C-01, REVIEW_REQUIRED, source_manifest

## Task 2: Latest Tinh omp field-test summary, success

### rollout_summary_files

- rollout_summaries/2026-09-27T05-37-22-gy0V-summarize_latest_tinh_package_test.md (cwd=C:\Users\tukum\Downloads\pdd-auto, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T12-37-22-01a0e15e-3451-7a71-a6ec-85cda24a79c1.jsonl, updated_at=2026-09-27T05:40:52+00:00, thread_id=01a0e15e-3451-7a71-a6ec-85cda24a79c1, newest report at commit 94ed0ad)

### keywords

- Tinh, omp, portable-package, fabricated-hashes, 25/25, 571623 rows, reports/2026-09-24-tinh-portable-package-omp-field-test.html

## User preferences

- when the user asked to “execute step by step with me as if we're running a test demo” -> pause at setup/message checkpoints, report hiccups, and ask before proceeding [Task 1]
- when asked for the “latest result” -> locate the newest dated report, lead with verdict and important finding, and state location/commit [Task 2]

## Reusable knowledge

- `REVIEW_REQUIRED` is a workflow verdict, not Verra approval, registration, or submission status. Preserve the registered VM0043 v1.0 basis; do not silently substitute v1.1. [Task 1]
- Independently recompute every recorded source fingerprint against its named file. Shipped `check_authored_pdd.py` and `review_records.py` did not catch 0/25 fabricated 58–62-character hashes; acceptance repair then verified 25/25 64-character digests. [Task 2]
- Keep workbook limitations explicit: two unreadable large workbooks left 571,623 rows unaccounted for; sources were read-only and not recalculated/resaved. [Task 2]

## Failures and how to do differently

- `check_authored_pdd.py` residual template headings and coverage conflict mean the authored demo is not clean acceptance; after any artifact edit, rerender and visually reinspect. Escalate C-01 workbook-column lineage conflict to VVB rather than mapping/recalculating silently. [Task 1]
- On Windows use `Get-ChildItem`/`Select-Object`; use explicit LibreOffice path and user temp rather than `C:\Windows\Temp`. Create a clean copy and `.venv`, not the archived reference, before checks. [Task 1]

# Task Group: Windows Office-file generation fallbacks
scope: Create/open small Excel or PowerPoint artifacts when native Computer Use cannot drive desktop Office.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=safe as a local fallback; verify Office install and treat process checks as weaker than visual inspection

## Task 1: Build and open playful Excel workbook, success

### rollout_summary_files

- rollout_summaries/2026-09-27T05-43-00-u7SR-create_and_open_fun_excel_workbook.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T12-43-00-01a0e163-5d67-7920-8e00-317781040895.jsonl, updated_at=2026-09-27T05:46:55+00:00, thread_id=01a0e163-5d67-7920-8e00-317781040895, launched successfully)

### keywords

- Excel, openpyxl, RANDBETWEEN, excel_fun_party.xlsx, Start-Process, Office16\\EXCEL.EXE

## Task 2: Create and open fun PowerPoint deck, success

### rollout_summary_files

- rollout_summaries/2026-09-27T06-02-23-L1DS-create_open_fun_powerpoint_deck.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T13-02-23-01a0e175-1b86-78c0-a430-c0ff80600544.jsonl, updated_at=2026-09-27T06:02:28+00:00, thread_id=01a0e175-1b86-78c0-a430-c0ff80600544, POWERPNT running)

### keywords

- PowerPoint, python-pptx, powerpoint_fun_sunday.pptx, POWERPNT, Start-Process

## User preferences

- when the user says “open excel and do something fun” -> a self-contained visual/interactive workbook is a reasonable default [Task 1]

## Reusable knowledge

- `openpyxl` 3.1.5 and `python-pptx` 1.0.2 were available; Excel and PowerPoint executables are under `C:\Program Files\Microsoft Office\root\Office16\`. Use direct generation then `Start-Process`. [Task 1][Task 2]

## Failures and how to do differently

- Native Computer Use exposed no desktop apps. Generate/launch as fallback, but distinguish `MainWindowTitle`/process evidence from visual file verification. New-file `apply_patch` requires proper `+` lines; avoid embedded JS or Unix shell syntax on PowerShell. [Task 1][Task 2]

# Task Group: Vietnam weekly workplan synthesis and Sheets reconciliation
scope: Build Vietnam-only candidate plans from Gmail/Drive, then separately reconcile against TSheets/Google Sheets completion formatting.
applies_to: cwd=C:\Users\tukum\Downloads\remote; reuse_rule=time-specific source evidence; read live sheet formatting before edits

## Task 1: Synthesize Phase 1 Vietnam candidates, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-38-XwkY-vietnam_weekly_task_plan_phase1_2026_09_27.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-38-01a0e1d3-a25e-7160-b4ee-14ad3cbc58fc.jsonl, updated_at=2026-09-27T07:45:38+00:00, thread_id=01a0e1d3-a25e-7160-b4ee-14ad3cbc58fc, Phase 1 only; Gmail plus Drive last-7-days synthesis, sheet untouched)

### keywords

- next-week-tasks_2026-09-27.md, Vietnam-only, Tung, Cong, Hang, Anh, Trang, Tinh, Unassigned, Gmail search_threads, Drive modifiedTime, subagent extraction, PYTHONIOENCODING=utf8

## Task 2: Phase 2 sheet update blocked by authentication, fallback partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-38-DFny-vietnam_workplan_phase2_auth_failure_fallback.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-38-01a0e1d3-a236-7f73-a9b4-40eb1da0bb30.jsonl, updated_at=2026-09-27T07:45:38+00:00, thread_id=01a0e1d3-a236-7f73-a9b4-40eb1da0bb30, fallback written; no sheet edit)

### keywords

- gws auth login, auth_method none, Access denied. No credentials provided., strikethrough, 2026-09-28, 46293, batchUpdate, GWS absolute path, Proposed Sheet Additions, 34 tasks

## Task 3: Synthesize Phase 1 candidates for week of 2026-09-13, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-DqEd-vietnam_weekly_task_plan_phase1_2026_09_13.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b97a-7761-835f-a82c9b91eeed.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b97a-7761-835f-a82c9b91eeed, candidates saved; Nike DPPA midweek deadline top blocker)

### keywords

- next-week-tasks_2026-09-13.md, Vietnam-only, newer_than:7d, subagent-extraction, Nike-DPPA, Hai-Phong, CEBA-Academy, GAP

## Task 4: Phase 2 sheet update via Sheets API with strikethrough-aware filtering, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-44-MRlY-vietnam_weekly_workplan_sheet_update_2026_09_14.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-44-01a0e1d3-b8c9-7030-8d7b-e4f3795af036.jsonl, updated_at=2026-09-27T07:45:44+00:00, thread_id=01a0e1d3-b8c9-7030-8d7b-e4f3795af036, new week row inserted and read-back verified)

### keywords

- gws sheets spreadsheets batchUpdate, insertDimension, strikethrough FALSE, date-serial 46278, GWS absolute path, node parse, Weekly

## Task 5: Synthesize Phase 1 candidates for week of 2026-09-20, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-YHfe-vietnam_weekly_task_plan_phase1_2026_09_20.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-b054-7873-8cf4-df966462ba8c.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-b054-7873-8cf4-df966462ba8c, candidates saved to next-week-tasks_2026-09-20.md; sheet untouched)

### keywords

- next-week-tasks_2026-09-20.md, Vietnam-only, gather-only, subagent digest, PYTHONIOENCODING=utf-8, tool-results slicing

## Task 6: Phase 2 sheet update fell back to markdown proposal on Sheets 403, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-Uypb-vietnam_weekly_workplan_2026_09_21_fallback.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-b02f-70f3-b88b-d08d6ee54ab1.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-b02f-70f3-b88b-d08d6ee54ab1, 46 tasks proposed in markdown; nothing written; superseded by Task 7)

### keywords

- Sheets 403 insufficient scopes, Proposed Sheet Additions, serial 46286, no strikethrough filter, failure fallback

## Task 7: Reconcile candidates and write verified 2026-09-21 row with 44 tasks, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-akZE-vietnam_weekly_workplan_2026_09_21_sheet_update.md (cwd=C:\Users\tukum\Downloads\remote, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-b01e-70f0-993a-be6c219d6b4e.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-b01e-70f0-993a-be6c219d6b4e, 44 tasks written 9/8/5/4/5/8/5 and read-back verified; blind proposal superseded)

### keywords

- 2026-09-21 row, 44 tasks, includeGridData read-back, before/after dumps, strikethrough runs, String.fromCharCode unicode workaround, live headers

## Task 8: Fix gws auth scopes, repair A2 date, rerun Phase 2, harden notify.py, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-Q7Z4-vn_weekly_gws_scope_fix_sheet_rerun_notify_harden.md (cwd=C:\Users\tukum, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-afb3-75a1-87e3-f648d7a40186.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-afb3-75a1-87e3-f648d7a40186, full-scope re-auth plus A2 46278->46279 fix plus notify classify hardening with 9 tests)

### keywords

- gws auth login full scopes, scope replacement, background localhost login, A2 date fix, p2_override.txt, notify.py classify, compute_target_monday, python -m pytest

## User preferences

- Vietnam weekly plans must be Vietnam-only, grouped by Tung/Cong/Hang/Anh/Trang/Tinh/Unassigned, with source, priority, and due date; retain uncertain/possibly-complete candidates with caveats for Phase 2 [Task 1]
- Phase 1 must gather evidence without Google Sheet edits; completion reconciliation is a separate Phase 2 operation [Task 1]
- when updating the sheet, the user said "USE THE SHEETS API, NOT CHROME" and "Do NOT use browser tools" -> use the `gws` CLI only for Google Sheets work [Task 4]
- when invoking gws, the user said to always invoke it by absolute path -> use GWS="/c/Users/tukum/AppData/Roaming/npm/gws", never rely on PATH [Task 4]
- when building the new row, the user said each cell is newline-separated `- task description (Owner)` bullets with first names, leave a column empty when nothing new applies, and "Do NOT invent tasks" [Task 4]
- when writing, the user said "Never append at the bottom; never duplicate a week row" -> top-insert at startIndex 1/endIndex 2 unless A2 already holds TARGET_DATE [Task 4]
- when saving Phase 1, the user said read the most recent next-week-tasks file first, mirror its headings, use the absolute Windows path, and report the file path plus a one-paragraph summary [Task 3]
- when working Sheets, the user instructed to use the Sheets API not Chrome and to not use browser tools -> honor it even when Sheets calls fail; write the markdown fallback instead of falling back to Chrome [Task 6]
- when Phase 1, the user said gather and synthesize only without touching the Google Sheet and to not judge what is already complete -> include uncertain items with likely-done flags for Phase 2 to reconcile [Task 5]

## Reusable knowledge

- Use targeted Gmail/Drive metadata searches and saved-result JSON/subagents when broad reads exceed output limits. Mirror the prior plan headings. [Task 1]
- Before any sheet edit: authenticate `gws auth login`; read the newest row with formatting, drop struck-through completed candidates, batch-write once, and read back date, uniqueness, strikethrough state, and prior-row preservation. [Task 2]
- Target sheet is 1JgAa0Ct4lcSAA4Lm1PLgQEcle82twp0YLArqInwRDd0 (2026 Vietnam Workplan), Weekly sheetId 0; TARGET_DATE 2026-09-28 is serial 46293. When python3 is missing (Microsoft Store stub Exit 49), compute serials with bash date arithmetic and check weekday with date -d +%A. [Task 2]
- Strikethrough semantics for this sheet: whole-cell effectiveFormat.textFormat.strikethrough or per-line textFormatRuns; STRIKETHROUGH MEANS DONE; blank rows inherit strikethrough from the row beneath, so new writes must explicitly set strikethrough FALSE with fields. Without an includeGridData read there is no completion signal; the fallback appended 34 tasks (B4 C7 D5 E4 F5 G7 H5) as Proposed Sheet Additions with (verify) flags. [Task 2]
- Credential diagnostics: GWS=/c/Users/tukum/AppData/Roaming/npm/gws; check auth status plus ls ~/.config/gws (client_secret.json present, credentials.enc/credentials.json missing with only .bak files means every Sheets call returns Access denied); do not restore .bak files automatically. [Task 2]
- Live header order is A Date | B Hai Phong Green | C KBC and CPI Industrial | D CEBA Academy | E GTB | F BizDev and Carbon | G REI, GAP and Peak | H Other; map to the real headers, not the brief order. Sheet dates are serials (date - 1899-12-30).days with DATE yyyy-mm-dd format. [Task 4]
- Strikethrough is the sole status record: whole-cell done versus per-line textFormatRuns; decode runs to slice which bullets are done. The verified write pattern is one batchUpdate (insertDimension then updateCells with strikethrough false plus DATE format), then an independent includeGridData read-back checking zero strikethrough on the new row, previous row byte-identical, and exactly one TARGET_DATE row. [Task 4]
- Oversized Gmail (50 threads) and Drive sheet reads exceed output limits; delegate parsing to subagents with explicit jq/python probe instructions, and full-read thin-snippet threads before finalizing. [Task 3]
- gws auth login REPLACES the grant: a narrow re-login silently drops unnamed scopes, so always re-auth with the full set the job needs (spreadsheets plus gmail.modify plus identity), run it in background, hand the user the localhost URL, and verify with real API calls plus credentials mtime, never status alone. Scope-string parses fine; an abandoned consent looks like a scope error. [Task 8]
- Week rows: newest week top-inserts at index 1 with DATE serial plus strikethrough FALSE and must explicitly clear formatting; TARGET 2026-09-21 is serial 46286 and row2 2026-09-14 is 46279, so a wrong-Sunday A2 gets fixed with a userEnteredValue-only batchUpdate. Verify by reading the actual sheet against independently computed serials, not by re-deriving the same buggy math. New rows map by live row-1 header names (order drifts between runs); CarbonSim logistics belongs under Hai Phong Green. [Task 7][Task 8]
- notify.py status must come from sheet read-back via classify(): phase non-zero means FAILED, no dates means UNVERIFIED never OK, 0 or 2-plus TARGET matches mean FAILED; compute_target_monday is strictly after today. Use the python -m pytest form since bare python -c import pytest is classifier-denied. [Task 8]

## Failures and how to do differently

- `gws auth status` was `auth_method: none` and calls returned `Access denied. No credentials provided.` Do not restore `.bak` credentials automatically or claim completion; use the appended `## Proposed Sheet Additions` fallback. [Task 2]
- Sheets writes are impossible non-interactively once scopes are missing: stop Sheets attempts after diagnosis and write the proposal instead of looping. With no includeGridData read there is no strikethrough signal, so drop only items the candidate file marks closed/obsolete and let the applier check the struck row before pasting. [Task 6]
- `python3` and `jq` are unavailable in the remote exec env; use `date +%s` arithmetic or node scripts for date-serial math and large-JSON parsing, and verify Monday math manually since `date -d "next monday 2026-09-13"` returned the same Sunday. Write helper output to a local file in the workdir, not /tmp. [Task 4]
- Drive shortcut files return {} on read; resolve the shortcut target or use the transcript/recording instead of treating {} as no content. [Task 3]

# Task Group: Hai Phong city-GHG analysis and visual artifacts
scope: Diagnose Hai Phong emissions/workbook issues and prepare visual, often bilingual, review artifacts grounded in source checks.
applies_to: cwd=C:\Users\tukum\Downloads\city-ghg; reuse_rule=checkout-specific and data-sensitive; revalidate all workbook figures and sharing settings

## Task 1: Verify 1A2 emissions anomalies and update artifact, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-Gy1X-hp_1a2_65gt_diagnosis_artifact.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a762-73d0-ab41-656221311601.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a762-73d0-ab41-656221311601, existing artifact updated)

### keywords

- 1A2.xlsx, 65631 Mt, LPG kg tonnes, City ouputs (cleaned), electricity-only, 1A1

## Task 2: Review Deliverable 1.2 BAU/reductions, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-s5WV-hp_1_2_hang_feedback_artifact.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a5fb-7780-87c6-916438c43079.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a5fb-7780-87c6-916438c43079, feedback artifact published)

### keywords

- BAU 26-30 vision 2050 & Reduction, 4357500, 1854050, dairy cows, DEC-008, 43.5%

## Task 3: Territorial split bilingual report, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-40-IMgG-hai_phong_east_west_split_options_report.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-40-01a0e1d3-a97f-7992-b9c9-5fa0b997548a.jsonl, updated_at=2026-09-27T07:45:40+00:00, thread_id=01a0e1d3-a97f-7992-b9c9-5fa0b997548a, version 2 bilingual)

### keywords

- east west, merged-city target, #vi, localStorage, Decision 117/QD-UBND, territorial split

## Task 4: Industrial-park VIDA/CPI/TIC synthesis, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-40-cPyC-hai_phong_49_parks_vida_wef_tic_artifact.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-40-01a0e1d3-a9e3-7ed1-a9f0-b15ef425931e.jsonl, updated_at=2026-09-27T07:45:40+00:00, thread_id=01a0e1d3-a9e3-7ed1-a9f0-b15ef425931e, published review; user review unconfirmed)

### keywords

- 49 parks, 913542 tCO2e, WEF TIC KPI Toolkit, Trang Due, Binh Giang, KCN sinh thai

## Task 5: Open and publish Deliverable 1.2 reports, success

### rollout_summary_files

- rollout_summaries/2026-09-28T04-10-55-kiBp-open_deliverable_1_2_and_push_reports.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\28\rollout-2026-09-28T11-10-56-01a0e635-6ab7-7950-aae3-0b3f47a0cfc7.jsonl, updated_at=2026-09-28T09:25:28+00:00, thread_id=01a0e635-6ab7-7950-aae3-0b3f47a0cfc7, reports pushed to main)

### keywords

- Deliverable 1.2, 2026-09-24-hp-1-2-feedback-hang.html, Start-Process, LastWriteTime, 5750416, pre-commit, pytest, data/incoming

## Task 6: Triangulation and gap-fill research brief for merged-city BAU, success

### rollout_summary_files

- rollout_summaries/2026-09-29T23-14-11-jEcp-hp_triangulation_gapfill_research_brief.md (cwd=C:/Users/tukum/Downloads/city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T06-14-11-01a0ef72-77dd-7680-9e6e-67a41ab385e9.jsonl, updated_at=2026-09-30T01:18:39+00:00, thread_id=01a0ef72-77dd-7680-9e6e-67a41ab385e9, 24KB brief delivered via chunked-write workaround)

### keywords

- Hai Phong, Hai Duong merger, BAU 2026-2030, triangulation, gap-fill, 1A2, IPPU steel, EDGAR ODIAC Climate TRACE, GPC BASIC, PDP8, research brief, DONE path

## Task 7: 1A2 sample-to-city extrapolation method validation, success

### rollout_summary_files

- rollout_summaries/2026-09-30T10-04-25-Q8iX-hp_1a2_extrapolation_method_validation.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T17-04-25-01a0f1c5-c4c0-74b0-a645-8c5e11798047.jsonl, updated_at=2026-09-30T10:22:39+00:00, thread_id=01a0f1c5-c4c0-74b0-a645-8c5e11798047, gap-fill plus top-down bounds recommended over percentile caps)

### keywords

- 1A2, extrapolation, expansion-factor, winsorization, gap-fill, Cochran-ratio, IPCC, GPC, TACCC, sensitivity-analysis, openpyxl, uv run python, P90 343x

## Task 8: Exhaustive 100-source 1A2 validation with Herdr handoff, success

### rollout_summary_files

- rollout_summaries/2026-09-30T11-24-03-Z4Cw-city_ghg_1a2_100plus_validation.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\30\rollout-2026-09-30T18-24-03-01a0f20e-adef-7611-a070-d1b8ac9c8eac.jsonl, updated_at=2026-10-01T03:18:03+00:00, thread_id=01a0f20e-adef-7611-a070-d1b8ac9c8eac, 100 counted sources with ledger plus synthesis and Herdr DONE report)

### keywords

- Hai-Phong-1A2, 100-sources, source-ledger, GPC-IPCC, CEADs, MECS, Herdr-handoff, w3C:p1, verbatim quotes, access_level

## Task 9: Trang 37-issue tool cross-check plus methodology-vs-standards review, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-Ff9h-hp_ghg_trang_crosscheck_methodology_review.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b5af-7f33-b775-186b90256f63.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b5af-7f33-b775-186b90256f63, two HTML reports published)

### keywords

- Trang 37 issues, cross-check HTML, methodology review, GPC BASIC+, Decree06 QD2626, IPCC Tier1 Tier2, openpyxl diff, gws drive files get, pypdf factor tables
## Task 10: Selective commit and push of HP 1A2 work to main, success

### rollout_summary_files

- rollout_summaries/2026-10-04T20-11-48-12oc-city_ghg_selective_commit_push_main.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\05\rollout-2026-10-05T03-11-48-01a1088b-4937-7c51-aa0d-a29db029935c.jsonl, updated_at=2026-10-04T20:16:11+00:00, thread_id=01a1088b-4937-7c51-aa0d-a29db029935c, 33 files committed as 30325f7 and pushed; scratch left uncommitted)

### keywords

- git commit push main, 30325f7, curated staging, uv run pytest, uv run ruff check, pre-commit hooks, write_stdin, origin/main

## Task 11: Oct-6 six-brief herdr research round for merged-HP 1A2, success

### rollout_summary_files

- rollout_summaries/2026-10-06T14-02-37-W8c2-city_ghg_1a2_six_briefs_exhaustive_research.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-02-37-01a11186-010d-7270-bc1f-04d1a5861aea.jsonl, updated_at=2026-10-06T14:08:04+00:00, thread_id=01a11186-010d-7270-bc1f-04d1a5861aea, all six briefs written with six herdr report-backs)
- rollout_summaries/2026-10-06T14-02-54-9Fom-hp_1a2_six_briefs_exhaustive_research.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-02-54-01a11186-42c3-7540-85cb-d7a1fce8c232.jsonl, updated_at=2026-10-06T14:09:28+00:00, thread_id=01a11186-42c3-7540-85cb-d7a1fce8c232, six-brief dispatch with citation contract and exhaustive-lite disclosure)
- rollout_summaries/2026-10-06T14-03-02-6sLz-city_ghg_hp_1a2_three_briefs_herdr_reportback.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-03-02-01a11186-6312-7020-a6c7-0877cb8ad835.jsonl, updated_at=2026-10-06T14:06:57+00:00, thread_id=01a11186-6312-7020-a6c7-0877cb8ad835, wrote unclaimed slugs after sibling audit)
- rollout_summaries/2026-10-06T14-02-48-DgIb-city_ghg_1a2_six_briefs_verify_reportback.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-02-48-01a11186-2c3f-7893-aba6-53d29ff8b20b.jsonl, updated_at=2026-10-06T14:06:29+00:00, thread_id=01a11186-2c3f-7893-aba6-53d29ff8b20b, verified six briefs present, no overwrite)
- rollout_summaries/2026-10-06T14-02-42-xo9i-hp_1a2_energy_facility_lists_supplement.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-02-42-01a11186-1600-7643-8bfc-4f0099b90778.jsonl, updated_at=2026-10-06T14:10:07+00:00, thread_id=01a11186-1600-7643-8bfc-4f0099b90778, non-colliding energy-facility-lists supplement)
- rollout_summaries/2026-10-06T14-01-57-eARB-hp_1a2_official_stats_corrections_research.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-01-58-01a11185-6733-7132-bb44-8e24c49ca90b.jsonl, updated_at=2026-10-06T14:10:59+00:00, thread_id=01a11185-6733-7132-bb44-8e24c49ca90b, partial: HP 2024 product lines found, HD year-end PDF and brief write-up pending)

### keywords

- HP-1A2 six briefs, r-stats r-energy r-plants r-guide r-cases r-methods, herdr report-back, Q-Qsec-D, territory hp_legacy hd_legacy, exhaustive-lite, sibling-coordination, Hoa-Phat 8.1Mt, CEADs, Rajkot 7pct

## Task 12: r-guide and r-methods deep primary-source briefs, success

### rollout_summary_files

- rollout_summaries/2026-10-06T14-13-42-o3ZJ-hp_1a2_data_gap_guidance_r_guide.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-13-43-01a11190-2873-7933-9b64-fd01f1aa045f.jsonl, updated_at=2026-10-06T15:04:43+00:00, thread_id=01a11190-2873-7933-9b64-fd01f1aa045f, b1-guidance brief from 36 opened primaries plus URL-compliance fix)
- rollout_summaries/2026-10-06T14-13-57-7pBF-hp_1a2_correction_methods_literature.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T21-13-58-01a11190-6425-77e2-8586-574a5589735b.jsonl, updated_at=2026-10-06T15:05:58+00:00, thread_id=01a11190-6425-77e2-8586-574a5589735b, b3-methods brief from 46 opened URLs plus URL fix)

### keywords

- b1-guidance, b3-methods, lane-identification, unexpanded-variable, Wayback fetch, PyMuPDF, fetch-log, IPCC GPC EDIMBUS, MECS, URL-compliance-fix

## Task 13: r-energy official energy/fuel-data brief with merged-city DEU census, success

### rollout_summary_files

- rollout_summaries/2026-10-06T15-01-03-waL9-hp_1a2_official_energy_data_r_energy.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T22-01-03-01a111bb-80cc-7143-af9a-e7d137101473.jsonl, updated_at=2026-10-06T16:00:23+00:00, thread_id=01a111bb-80cc-7143-af9a-e7d137101473, 106KB brief with 248-row appendix plus herdr report-back)

### keywords

- r-energy, QD3568, DEU-2024, TOE, merged-city, 248-facilities, 8.14Mt-central, congbao, dataenergy, GSO-balance, BUR3

## Task 14: r-cases city/region case-studies brief with CEADs and merger precedents, success

### rollout_summary_files

- rollout_summaries/2026-10-06T15-01-31-v9vk-hp_1a2_b2_city_case_studies.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T22-01-31-01a111bb-ee3b-7bf3-8da8-e9a27e635bb2.jsonl, updated_at=2026-10-06T22:34:18+00:00, thread_id=01a111bb-ee3b-7bf3-8da8-e9a27e635bb2, 74KB/518-line brief plus 50-line JSONL ledger plus herdr report-back)

### keywords

- r-cases, CEADs, ADS-output-ratio, Mumbai-baseline, Auckland-Montreal-merger, GPC-CIRIS, EDGAR-ODIAC, Quezon-unit-slip

## Task 15: r-plants plant-level sources brief plus GEM sweep completion via public geojson, success

### rollout_summary_files

- rollout_summaries/2026-10-06T15-01-19-v3oN-hp_1a2_plant_level_sources_gem_sweep.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\06\rollout-2026-10-06T22-01-20-01a111bb-c08c-73a3-ae4b-d4a604d84765.jsonl, updated_at=2026-10-06T21:59:29+00:00, thread_id=01a111bb-c08c-73a3-ae4b-d4a604d84765, 38KB a3 brief plus GEM category sweep plus unit-corrected geojson completion with TOE-vs-MW verdict)

### keywords

- r-plants, GEM sweep, gem.wiki 403, public geojson, unit-corrected, TOE vs MW, Hoa Phat Hai Duong, clinker 10.18Mt, QD3568 auxiliary


## Task 16: Lane A BAU methods/tools research brief with 16-source ledger, success

### rollout_summary_files

- rollout_summaries/2026-10-08T00-51-42-kBXl-hp_bau_methods_tools_lane_a.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\08\rollout-2026-10-08T07-51-43-01a118fe-9f3e-78e0-af50-2bd4f0bbfe63.jsonl, updated_at=2026-10-08T01:20:08+00:00, thread_id=01a118fe-9f3e-78e0-af50-2bd4f0bbfe63, 16-source brief plus ledger plus herdr report-back)

### keywords

- hp-bau-methods-tools, lane-a, GPC BASIC+, Mitigation-Goal-Standard, Decree-06, LEAP, CURB, PDP8, grid-EF, herdr-report-back

## Task 17: Lane B BAU reference-cases brief with 17-source ledger, success

### rollout_summary_files

- rollout_summaries/2026-10-08T00-51-42-JWbd-hp_bau_reference_cases_lane_b.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\08\rollout-2026-10-08T07-51-43-01a118fe-9f3e-78e0-af50-2be412447077.jsonl, updated_at=2026-10-08T01:13:25+00:00, thread_id=01a118fe-9f3e-78e0-af50-2be412447077, 17-source brief plus ledger plus herdr report-back)

### keywords

- hp-bau-reference-cases, lane-b, NDC-2022-BAU, Da-Nang-BaU, Tangshan-LEAP, GPC-1.1, OpenAlex, Wayback-CDX, jina-reader, herdr-report-back

## Task 18: Lane C BAU forecast-calc brief with 18-source ledger, success

### rollout_summary_files

- rollout_summaries/2026-10-08T00-52-51-QkZN-hp_bau_forecast_calc_lane_c.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\08\rollout-2026-10-08T07-52-51-01a118ff-ad66-7f31-8006-4b4748f6cac7.jsonl, updated_at=2026-10-08T01:13:13+00:00, thread_id=01a118ff-ad66-7f31-8006-4b4748f6cac7, 18-source brief plus ledger plus herdr report-back)

### keywords

- hp-bau-forecast-calc, lane-c, PDP8-Decision-768, MONRE-1726-grid-EF, Hoa-Phat-Hai-Duong, cement-122Mt, KH-4729, WEM-WAM, IPCC-Approach-1, herdr-report-back

## Task 19: BAU evidence-pack download recovery plus Drive upload of 55 files, success

### rollout_summary_files

- rollout_summaries/2026-10-08T03-24-51-AGLH-bau_evidence_pack_download_upload_drive.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\08\rollout-2026-10-08T10-24-52-01a1198a-d799-7c11-9fe4-1f14de779cd5.jsonl, updated_at=2026-10-08T04:03:20+00:00, thread_id=01a1198a-d799-7c11-9fe4-1f14de779cd5, 51-file pack plus Drive upload of 55 files plus herdr report-back)

### keywords

- BAU-evidence-pack, sources_index, IGES-mirror, datafiles-chinhphu, ScienceDirect-signed-URL, gws-drive-upload, browser-control-fetch, drive_ids

## Task 20: 1A2 hybrid-method standards, 10pct-cutoff, and threshold-justification briefs, success

### rollout_summary_files

- rollout_summaries/2026-10-08T08-40-19-SRjr-hp_1a2_hybrid_standards_threshold_research.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\08\rollout-2026-10-08T15-40-20-01a11aab-a85a-7e70-b07f-7c2438440cc9.jsonl, updated_at=2026-10-08T09:45:41+00:00, thread_id=01a11aab-a85a-7e70-b07f-7c2438440cc9, three briefs written and verified UTF-8 plus END-OF-REPORT)

### keywords

- hp-1A2-hybrid-standards, 10pct-cutoff-sources, threshold-justification, hybrid_rows_extract, Hidiroglou-Berthelot, expansion-factor-10x, GWP-AR5-28-265, Decision-18-CMA-1, Phan-tich-nguong, scratch_threshold

## Task 21: SCATTER Phase 1 Acquire blocked-final with full evidence trail, success

### rollout_summary_files

- rollout_summaries/2026-10-09T04-36-00-cecf-scatter_phase1_acquire_blocked_final.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T11-36-01-01a11ef2-54de-79a0-965d-33afa23ac44f.jsonl, updated_at=2026-10-09T04:48:12+00:00, thread_id=01a11ef2-54de-79a0-965d-33afa23ac44f, publisher-only acquire, blocked-final with parked-domain proof)

### keywords

- SCATTER, scattercities.com parked-domain, Anthesis 404, C40 login-wall, Wayback-CDX, gov.uk search nil, chrome-devtools-axi headed session, blocked-final, publisher-only, UK-BEIS-unfit-VN

## Task 22: GACMO v2.3 Hai Phong BAU tool comparison Phases 1-4 with Hang vs corrected runs, success

### rollout_summary_files

- rollout_summaries/2026-10-09T04-36-00-rjz7-gacmo_hai_phong_bau_comparison.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T11-36-01-01a11ef2-54df-7021-a297-c7ff1e554815.jsonl, updated_at=2026-10-09T05:44:16+00:00, thread_id=01a11ef2-54df-7021-a297-c7ff1e554815, acquired mapped ran compared plus review fix)

### keywords

- GACMO-v2-3, gacmo-v2-3.xlsm SHA256, Excel-COM AutomationSecurity-3, Growth-col-J staging, BAU-power-postprocess, RunA-Hang-15.2pct, RunB-corrected, territorial-vs-BASIC-plus, Unblock-File, utf-8-sig-BOM, vendor-gitignored

## Task 23: Top-down inventory cross-check with EDGAR plus Climate TRACE and Drive upload, success

### rollout_summary_files

- rollout_summaries/2026-10-09T08-46-51-aFxS-inv_topdown_hai_phong_crosscheck_and_drive_upload.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T15-46-52-01a11fd7-fec7-7e22-b0f6-5ec62605f838.jsonl, updated_at=2026-10-09T13:06:05+00:00, thread_id=01a11fd7-fec7-7e22-b0f6-5ec62605f838, cross-check plus 12-file Drive upload)

### keywords

- inv-topdown, EDGAR-UCDB-2026, Climate-TRACE-v6-assets, GADM-PIP, geoBoundaries-gbHumanitarian, EDGAR-CO2-only, AR5-28-265, gws-drive-upload-cmd-batches, tar-xlsx-extract, like-for-like-CO2

## Task 24: LEAP licence-bypass refusal with compliant fallbacks then session-output deletion, partial

### rollout_summary_files

- rollout_summaries/2026-10-09T14-03-58-hv27-leap_license_bypass_refusal_and_deleted_fallback.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T21-03-59-01a120fa-5233-79e3-bde3-e0ae837a85c7.jsonl, updated_at=2026-10-09T14:24:04+00:00, thread_id=01a120fa-5233-79e3-bde3-e0ae837a85c7, bypass refused, fallbacks deleted on user request)

### keywords

- LEAP-26.7.3-evaluation-mode, SEI-licence-denial, bypass-refusal, beneficiary-institution, build_leap_bau.py, session-output-deletion, single-file-delete

## Task 25: LEAP Hai Phong BAU acquire-map-build Phases 1-3 to evaluation-mode block, partial

### rollout_summary_files

- rollout_summaries/2026-10-09T04-36-00-ewZ2-leap_bau_acquire_map_build_eval_block.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T11-36-01-01a11ef2-54e5-7862-87ac-c6efe6144128.jsonl, updated_at=2026-10-09T08:44:05+00:00, thread_id=01a11ef2-54e5-7862-87ac-c6efe6144128, acquire plus map success, build blocked on eval-mode save lock, licence bypass refused)

### keywords

- LEAP-26.7.3, leap.sei.org gated-download, setup64.exe SHA256, LEAPApplication-COM, AddTechnology-6-args, LEAP-Areas-OneDrive-path, evaluation-mode-save-disabled, inputs.csv-67-rows, GRDP-elasticity-0.7, clinker-capacity-x-utilisation

## Task 26: IPCC Tier-1 Energy plus IPPU cross-check of Trang tool plus Drive upload, success

### rollout_summary_files

- rollout_summaries/2026-10-09T08-46-49-XTFL-inv_ipcc_tier1_crosscheck_drive_upload.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T15-46-50-01a11fd7-f7b8-7d43-ad7d-583e151b9c91.jsonl, updated_at=2026-10-09T13:00:15+00:00, thread_id=01a11fd7-f7b8-7d43-ad7d-583e151b9c91, tier-1 cross-check plus 17-file flat Drive upload)

### keywords

- inv-ipcc, IPCC-Inventory-Software-v2.98, 2006GL-2019-Refinement, Tier-1-defaults, clinker-0.51-CKD-1.02, BOF-1.46-EAF-0.08, run_tier1.py, results.csv-22-rows, drive_upload.py-flat-manifest, VIE_HPH_GHG_Tool-primary

## Task 27: CIRIS 2.6 whole-city plus 1A2-hybrid cross-check of Trang inventory plus Drive upload, success

### rollout_summary_files

- rollout_summaries/2026-10-09T08-46-49-aHbe-inv_ciris_ciris_crosscheck_1a2_drive.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T15-46-50-01a11fd7-f7b8-7d43-ad7d-58123dcdba74.jsonl, updated_at=2026-10-09T13:05:51+00:00, thread_id=01a11fd7-f7b8-7d43-ad7d-58123dcdba74, whole-city plus 1A2 checks plus 72-file flat Drive upload)

### keywords

- inv-ciris, CIRIS-2.6-Standard-Light, C40-GPC-BASIC-plus, Report-SUMIFS-A=T, Results_Summary-C12, Excel-COM-calc-sheets-only, M14-NO-clear, NL-pivot-surveyed-fuels, LPG-kg-as-tonnes-M1501, 1A2-CHECK.md, results.csv-20-rows

## Task 28: AFOLU-Waste IPCC worksheet cross-check of Trang tool plus Drive upload, success

### rollout_summary_files

- rollout_summaries/2026-10-09T08-46-50-C0ea-inv_afolu_waste_crosscheck_and_drive_upload.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\09\rollout-2026-10-09T15-46-50-01a11fd7-f940-70c1-9499-d1bffff4365e.jsonl, updated_at=2026-10-09T13:02:12+00:00, thread_id=01a11fd7-f940-70c1-9499-d1bffff4365e, AFOLU-waste cross-check plus 26-file Drive upload after duplicate reconcile)

### keywords

- inv-afolu-waste, IPCC-2006-Vol4-Vol5-worksheets, Waste-Model-FOD, run_model.py, AFOLU-564368t-unreported, rice-EFc-1.30, manure-Tier1-vs-Tier2, landfill-DOCf-k, UPLOAD.md-manifest, gws-Python-subprocess

- Related skill: skills/exhaustive-ledger-research/SKILL.md

## User preferences

- for analysis/review, "less word more visual" and an HTML artifact means concise charts, claim tables, options, and a reviewable published page [Task 1][Task 2]
- when the user says "Update existing," preserve the existing artifact URL; when they say "have it available upon toggle," put English/Vietnamese in the same artifact with a switch and `#vi` deep link [Task 1][Task 3]
- when a brief says read-only grounding, the user said "Do not edit code, data, or the workbooks" -> keep the run read-only and only add research/*.md [Task 6]
- when finished with a brief run, the user said reply with only "DONE <path>" -> reply with the minimal DONE line and no extra summary [Task 6]
- when a brief demands exhaustive evidence, the user expects exact counted-source compliance and machine-checked quotes: "At least 100 distinct sources actually opened and read" and "Never mark something verified that you did not open" -> fetch and open every source, record access_level, and verify each quote against fetched text [Task 8]
- when denominators are known-dirty, the user expects quoting only from files without inventing numbers -> reuse the G1-G10 anchors and cite file provenance [Task 8]
- when a URL fails, the brief says "If a URL fails, say so and do not use it as evidence" -> record failures separately and substitute verified open copies with a note, never fabricate [Task 8]
- when the user says "Report to claude agent herdr tab same space once done" -> agents inside Herdr (HERDR_ENV=1) locate the same-workspace Claude tab and use herdr agent prompt as the completion signal [Task 8]
- when verifying email feedback, the user said: "get the files and her comment to cross check using whatever tool that you have like gws cli or others to them produce an HTML report" -> retrieve Gmail/Drive autonomously via available CLIs and deliver an HTML report (local plus artifact link) [Task 9]
- when asking for a broader view, the user said: "take a step back and review the calc methodology for the tool to understand match with interntional standard in this domain" -> deliver a three-layer verdict with a gap register ordered by materiality [Task 9]
- when running a herdr-dispatched brief worker, the user said: "Work autonomously without asking questions; finish by running the herdr report-back command in 00-common.md" -> run end-to-end with no clarifying questions and finish with exactly one herdr agent prompt city-claude "[<name> DONE] research/2026-10-06_<slug>.md ..." with no --wait then stop [Task 11][Task 12]
- when Statistics Office data is declared FINAL with no chance to ask for corrections, the user required correction/validation only from OTHER public/official documents or defensible methods -> never propose re-asking the SO; freeze the SO table, log raw, and build outside anchors with an audit trail [Task 11]
- when parallel brief workers share research/2026-10-06_hp-1A2-*.md outputs, the user coordination implied leaving sibling files intact -> list research/ first, write only unclaimed or non-colliding supplement slugs, and verify presence plus structure instead of blind rewrite [Task 11]
- when doing city-ghg 1A2 research, the user required via 00-common.md that every number carry value, unit, period, territory (hp_legacy/hd_legacy/merged/national), exact URL, page/table, verbatim quote, and status Q/Q-sec/D with formula; never invent numbers [Task 11][Task 12]
- when doing ROUND2 lane research in city-ghg, the brief required ">=30 distinct primary sources actually opened (issue-2), every bullet answered with quoted figure or marked searched-not-found, fetch log URL->OK/failed, Q/Q-sec/D tagging, 10-line exec summary plus Recommended use table" -> meet that bar before finishing, not a snippet pass [Task 14]
- when assigned a lane (for example b2 r-cases), the instruction was "Stay in YOUR lane: read only 00-common plus YOUR task, do not read/write/verify other agents briefs, do not spawn helpers that write files, one herdr report-back" -> respect file ownership and never touch sibling briefs [Task 14]
- when geojson rows were treated as plants, the user flagged they are UNITS and required re-aggregation by status with unit counts/start years plus a TOE-vs-MW arithmetic verdict stated plainly -> aggregate units-of-m per tracker and state fuel-input usability explicitly [Task 15]
- when completing a parallel BAU research lane, Done required: "brief and sources.jsonl written with 12-18 verified credible sources, and the herdr report-back command executed" -> treat all three outputs as mandatory for lane completion [Task 16]
- lane file-ownership rule: "Do NOT edit any existing file in the repo. Write only your own output files" plus "Do not commit" -> lane agents only add their own research brief plus sources ledger and commit nothing [Task 16][Task 17][Task 18]
- when Cloudflare blocked direct fetches, the user said: "try browser control for blocked sites" -> on Cloudflare or bot-blocked downloads prefer real visible-browser fetch over curl, Playwright, or Firecrawl retries [Task 19]
- when evidence HTML was updated externally, the coordinator said: "Upload the current version; if you already uploaded it, update that Drive file in place (gws drive files update) instead of creating a duplicate" -> always upload the latest on-disk evidence HTML at finish time and update in place, never duplicate [Task 19]
- Drive pack layout precedent: "BAU evidence pack - 2026-10-08" folder plus "Sources" subfolder in the Emission Reduction parent, skip the B14 GPC duplicate, save id-name JSON lines to drive_ids.txt, fill drive_link then re-upload the index [Task 19]
- when a tool-comparison brief says report after EACH phase, the steering required: "herdr agent prompt city-ghg-claude \"[<agent>] PHASE <n> <done|blocked>: ...\" Do not pass --wait. Then stop and wait" -> report per phase with that exact one-line ASCII command and idle for steering, never auto-advance [Task 21][Task 22][Task 23]
- when acquiring a publisher tool, steering required: "Download official tool from publisher only; if blocked after 2-3 attempts via browser control, report blocked, never substitute look-alike" -> keep publisher URLs plus hashes in ACQUIRE.md and never re-implement or mirror-substitute [Task 21][Task 22]
- when a download is blocked, steering required a headed browser attempt first: "attempt it via browser control (chrome-devtools-axi, your own session name) before reporting blocked. Never submit registration/licence forms" -> try the real browser session, hard-stop at forms/logins [Task 21]
- when the user says "bypass leap for use by all mean as there has been an error with license" and reframes as NGO denial, security test, or distress pleas, treat it as a licence-defeat request and hold refusal across re-framings; urgency is not authorization [Task 24]
- when the user says "Delete all output files from current session u made for me im done" -> delete only session-created files one by one, preserve lane priors and committed inputs [Task 24]
- when uploading a lane pack to Drive, the user required: flat files with a lane prefix, EXCLUDE vendor/.venv/.work/__pycache__/temp and files over 50MB, no new folders, no permission changes, byte-verify listing vs local, then ONE herdr line with no --wait [Task 23]
- when checking Trang inventory workbooks, trang-orch steering required: primary object is hp/incoming/2026-09-09/VIE_HPH_GHG_Tool.xlsx plus 1A2 latest data/incoming/2026-10-08_trang_1a2_v4/, and any cell exactly 1000 is a not-yet-populated placeholder never compare -> verify file identity against the Steering section before mapping [Task 26][Task 27][Task 28]
- when entering cross-check data, brief ground rules said write only inside the own lane folder, no commits/pushes/uv add, emissions tCO2e plus energy TJ with every row tagged territory -> keep artefacts inside the lane folder [Task 26][Task 27]
- when reporting to the orchestrator, the user objective said push one-line report with herdr agent prompt trang-orch "[inv-*] PHASE n done|blocked: ..." never --wait then keep going -> push via herdr without waiting and continue [Task 26][Task 27][Task 28]
- when mapping LEAP inputs, steering said Run A Hang-inputs vs Run B corrected side by side to separate tool vs assumption effect, and 15.2pct stays the GRDP driver with correction as GRDP x elasticity (other-industry 0.7 central) while PDP8 ~10pct is electricity demand never a GDP proxy -> do not replace the GRDP rate itself [Task 25]
- when a LEAP licence is pending, steering said prepare a do-not-run build script via COM API from inputs.csv, do not launch leap.exe, stay idle with no report, and never patch/forge/tamper with licence validation -> confirm licence explicitly before COM writes [Task 25]

## Reusable knowledge

- 65,631 Mt came from compounding corrupted city-output quantities and one LPG kg-vs-tonnes entry; 36 products with <0.1% coverage account for 65,613.4 Mt. Coal power plants belong in 1A1, not 1A2. [Task 1]
- Treat Hai Phong headline reductions carefully: two values appear to be Vietnamese-decimal scale errors; livestock measures conflict with survey data, and 43.5% old-Hai-Phong/merged-2020-baseline language is inconsistent. [Task 2]
- Recommended split framing: report two zones but retain one merged-city compliance target; zone effort shares are non-binding and transparent. 49/24/14 industrial-park counts do not reconcile, so request an authority name-mapping key before park-level intensity. [Task 3][Task 4]
- Find the current Deliverable 1.2 report by recursively sorting `reports/` HTML files by `LastWriteTime`, then open it with `Start-Process`. The 2026-09-28 publish commit was `5750416`; validate publication with matching `HEAD`, `origin/main`, and clean `git status --short --branch`. [Task 5]
- Curated push pattern for mixed worktrees: separate the intended reports/research/scripts set from scratch helpers, verify with uv run pytest -q plus scoped uv run ruff check on tracked paths, stage the curated set only, and confirm the push with git status plus git log showing in sync with origin/main; commit 30325f7 covered 33 files. [Task 10]
- Source-of-truth precedence starts at context/cooperation-content-2026.md then context/decisions/**; DEC-001 base year 2025, DEC-003/008 reconciled merged 2020 baseline, Wave 2 Hai Duong due 10 Oct, gates 31 Oct / 31 Dec. [Task 6]
- The 1A2 estimator is a per-product separate ratio E_city(p)=E_sample(p)*F(p) with F=Q_city/Q_sample over 181 eligible products; the firm panel is a non-probability sample with no design weights, so all totals are model-dependent and need external anchors (energy-survey direct sum 7.7-8.1 Mt floor plus fuel-supply Reference Approach ceiling). [Task 7]
- Workbook ground truth (ver3 30 Sep): uncapped headline 4,279,097,331 tCO2e; global caps P80 26.27->6.64Mt / P85 88.06->9.42Mt / P90 343.36->14.13Mt / P95 1048.29->19.68Mt; dropping 66 abnormal codes deletes 2.67Mt measured including steel-bar 24100410 2,173kt. [Task 7]
- Recommended ranking: D+F (gap-fill floor1+gate10 plus top-down bounds) primary near 8.0Mt flat 1.02x across gates; E pooled ratio cross-check; G robust estimation post-Dec upgrade; A/B/C percentile and fixed caps as sensitivity fan only. P90 is acceptable only with 5 conditions met (clean first, band not point, floor measured, fuel-balance bound plus pending-verification line, documented as custom per IPCC Vol1 Ch5). [Task 7]
- Design weights come first (MECS certainty weight 1, UNSD SBR gross-up) with turnover-ratio fallback (ONS register turnover); coverage above 100 percent means weight 1, keep measured, and reconcile. Sample above city is self-representing, never dropped. [Task 8]
- Trang cross-check method: pull her reply (Gmail id 1a08fe2f988a4d77 in thread 19eb5a630719ac67) plus feedback and tool workbooks via gws drive files get to scratchpad, dump the check sheet with openpyxl (counts were 14 fixed / 14 disagreed / 9 need-info), cell-by-cell diff the workbooks, verify factors against IPCC PDFs via downloaded-file pypdf extract (WebFetch returns unusable binary), and deliver a local plus artifact-link HTML report. [Task 9]
- Cross-check verdicts worth reusing: all 14 fixed genuinely fixed with totals 15.30Mt to 15.88Mt matching added AFOLU rows and rice 605,682 tCO2e as the largest AFOLU term; 13 of 14 disagrees correct (waste shares not EFs) with issue 13 invalid (1A4 biomass CH4 should be 300 not 30); transport road diesel 3.9/3.9 and waterway 7/2; landfill 2021-2025 repeats 2020; email swapped the 14/9 counts versus the sheet 9/14; extra finds were 4C1 plastics-as-pure-plastic overstatement at 38 percent, garden k 0.03 versus 0.17, removed grid column, residential NE. [Task 9]
- Methodology verdict: Decree06/QD2626 aligned and IPCC2006 Tier1 (plus Tier2 landfill/rice/forest) aligned, GPC BASIC+ partial by design with no scope split while the engine holds the GPC crosswalk; high completeness gaps are 3C4/3C5, 2F, 1A4b, 3B conversions; weakest notes are cement-from-cement, steel 0.06 versus 0.08, missing landfill OX, cropland soil, manure mapping, and the N=2000 ratio estimator needing a write-up; electricity/territory/uncertainty columns were missing before Wave1 19-Sep. [Task 9]
- Related skill: skills/exhaustive-ledger-research/SKILL.md
- GEM category sweep: open EVERY Category page for cement/steel/coke/coal/gas/lime/glass/ceramics/fertilizer/ports/LNG, keep HP/HD entries with full field set plus quotes, flag missing/misplaced; when gem.wiki 403s, finish via public tracker geojson from interim-maps configs on the CDN, filtering country-area1=Vietnam with point-in-polygon and NFKD accent normalization. [Task 15]
- geojson rows are UNITS not plants: re-aggregate as operating/construction/announced/cancelled with unit counts and start years in NxSIZE=TOTAL form; never mix MW/Mt/ttpa across trackers; dedupe gmet mine mirrors. [Task 15]
- QD 3568 TOE cannot be total fuel input: 3440MW operating coal needs 3.76-5.67M TOE at normal CF/heat-rate versus 0.266M listed (implied CF 3.9 percent absurd), so treat it as auxiliary/admin basis and never as 1A1 activity. [Task 15]
- Cong Thanh Cement Kinh Mon (name-noneng Thanh Cong 3) equals 248-list Thanh Cong III 40819 TOE; do not double-count. [Task 15]
- Oct-6 1A2 state: survey floor 7.7 MtCO2, corrected total ~9.37 Mt (range 8.90-10.01), iron and steel ~4.4-4.7 Mt, non-metallic ~1.5-2.5 Mt, 244 products; six briefs live at research/2026-10-06_hp-1A2-{official-stats-corrections, official-energy-data, plant-level-sources, data-gap-guidance, city-case-studies, correction-methods-literature}.md plus supplement research/2026-10-06_hp-1A2-energy-facility-lists.md; each starts with a 10-line executive summary and ends with a Recommended use table. Do not repeat prior anchors (research/2026-10-04_hp-1A2-past-reference-data.md, research/2026-10-06_hp-1A2-reference-outputs.csv, reports/2026-10-06-hp-1A2-city-issues.json); build on them. [Task 11]
- Key bounds: HPG 2024 national crude steel 8.1 Mt (Q-sec via cafef.vn citing the HPG annual report) caps HD steel rows; Dung Quat 2.8->5.6 Mt/yr is Quang Ngai so excluded from hd_legacy; HPG Hai Duong Kinh Mon is hd_legacy; merged cement plausibility ceiling ~12 Mt/yr (Hoang Thach 4 Mt/yr plus VICEM HP); HP cement 4633/4248/3846 kt for 2019/20/21; HD clinker-plus-cement 7956/7311 kt over 11M2023/24; GSO national bricks 10576M and garments 6.1bn bound absurd city rows. Corrected unit-slip values win only on same-territory match within ~15 percent, else carry a range. [Task 11]
- Facility-energy lineage: Decision 13/2024/QD-TTg signed 13 Aug 2024 lists 2,166 facilities for 2024 GHG inventory due before 31 Mar 2025 (threshold at least 3,000 tCO2e or 1,000 TOE); annual designated-energy-user lists publish before 31 Mar per Decree 21/2011 Art.9 (threshold at least 1,000 TOE or 3,000,000 kWh); per-enterprise TOE lives in dataenergy.vn/DONRE filings, not in the published decisions; 2026 MAE draft adds ~540 facilities toward ~2,705 feeding the ETS pilot. Keep electricity and IPPU cement process out of 1A2; national 1A2 was 38,248.11 ktCO2e in 2016 (BUR3 Table 2.4). [Task 11]
- Deep-brief fetch workflow that beat the walls: fetch scripts with browser UA plus retries plus Wayback id_ fallback (web.archive.org/web/<ts>id_/<url>), PyMuPDF extraction, fetch log kept, downloads in a fresh scratchpad/fetch-<name>/ dir outside the repo, python run with python -I; HP yearbook product tables are not posted online so pivot to monthly/annual KTXH press releases via the sitemap-vi.news.xml enumeration; haiduong.gov.vn direct fetch fails so use Wayback CDX narrowed to /2024* or /2025* year folders (broad queries 504/timeout). If a page stays unfetched, list the URL with its exact pull target rather than inventing numbers. [Task 11][Task 12]
- r-guide lane result: decision table mapping unit slips, ambiguous, missing, sample-only, merger, and final-unrevisable cases to IPCC Vol.1 Ch.2/3/5/6 plus Vol.2 Ch.2, GPC H/M/L plus NE/IE/NO/C plus downscaling plus base-year recalculation, Eurostat EDIMBUS/UNECE plus UN IRES/ESCM, and Vietnam Dec 2626/QD-BTNMT plus Dec 06/2022/ND-CP plus Circ 17/2022/TT-BTNMT plus MOIT MRV; the inventory must show the reported table plus a correction annex plus uncertainty, never a silent overwrite. r-methods ranked pipeline: ratio/unit-value/cross-period edits, plant-sum replacement for steel/cement, ratio/regression/calibration re-expansion, CEADs downscaling fallback, gridded guardrails, IPCC Approach 1/2 Monte Carlo range; most transferable city cases are CEADs output-share downscaling, Rajkot 7 percent reconciliation, and merged-boundary base-year recalculation. [Task 12]
- r-energy result: merged-city DEU 2024 is QD 3568/QD-UBND 29/8/2025 with 248 facilities (234 industry, 3 transport, 11 construction) totalling 3,287,600 TOE; manufacturing excluding power 2,991,221 TOE (231 sites) converts to about 125,236 TJ and roughly 8.14 Mt CO2 central (6.7-9.0 Mt band over 40-20 percent electricity share), supporting the corrected 9.37 Mt over the 7.7 Mt floor. DEU sums are lower bounds (smallest entry near 1,025 TOE). National DEU 2023 QD 1011/QD-TTg pre-merger split: Hai Duong 103 sites 2,565,662 TOE, Hai Phong 132 rows 1,038,036 TOE. QD13/QD01 TOE columns are not summable (An Phat xanh 11,442,921 plus Thuan Phat 2,111,850 plus PCC Luc Xuong 1,163,459 TOE implausible; Hoa Phat 1,209 TOE versus DEU 727k-1,396k). City approved inventory QD 1772/QD-UBND 09/6/2025 gives hp_legacy 2020 20,882,410 tCO2e. National anchors: BUR3 2016 1A2 38,248 ktCO2e, GSO Yearbook 2025 energy balance 2024 industry-plus-construction 44,848.5 ktoe with electricity 27.26 percent. [Task 13]
- r-cases result: CEADs city method is the citable precedent for HP 244-product extrapolation (ADS enterprises scaled by whole-industry/ADS output ratio; Mi et al: no energy balance table for most Chinese cities, only 15/218 complete in 2015). Mumbai fix-the-baseline precedent revised 2019-20 23.42 to 26.75 MtCO2e (plus 14.2 percent) via 15 agencies in-house with C40 guidance. Merger rule: Auckland recalculates prior inventories each cycle, Montreal holds agglomeration-wide consistency across demerger, China gridded series re-standardises to GS(2024)0650. Guardrails: C40 GPC versus EDGAR R2 0.80 versus ODIAC R2 0.72; Tangshan national 53-75 percent low for heavy-industry cities. Quezon Eco-Profile Ch.5 prints kg as tons (transport 709,806,272.66 in tCO2e column), precedent for unit-slip restatement. [Task 14]
- Discovery when search is blocked: go direct to enumerable official endpoints (congbao.chinhphu.vn viewer plus congbaocdn direct PDF, luatvietnam.vn full HTML, dataenergy.vn danh-sach index, cdn.haiphong.gov.vn, Wayback id_ copies) instead of general web search; open 40-plus primaries via curl/python urllib with browser UA plus retries plus Wayback 2024id_ fallback into scratchpad/fetch-<name>/ with python run via python -I. [Task 13][Task 14]
- Oct-8 BAU lane verdicts for the Hang workbook: stop single compound GRDP for 1A2 and IPPU, use capacity and physical drivers plus an elasticity band; territorial total is Scope 1 only, never sum Scope1+Scope2 over the same generation; replace Scope2 x1.15 with the MONRE declining grid-EF trajectory; baseline is with-existing-measures with low, central, and high bands plus sensitivity and recalculation on base-year change [Task 16]
- BAU reference numbers: Vietnam NDC 2022 Update BAU 284.0 Mt (2014) to 927.9 Mt (2030), CAGR 7.68 percent per year with energy 171.6 to 678.4 at 8.97 percent; unconditional minus 15.8 percent and conditional minus 43.5 percent vs BAU; Da Nang BaU 2.7 Mt (2013) to 10.7 Mt (2030) CAGR 8.44 percent vs 9.7 percent GDP implying elasticity near 0.87; HP 15.2 percent per year GRDP-compounded BAU is 1.7x to 5.6x the benchmark band and traces to the Hai Phong GRDP 16.03 percent 2018 figure [Task 17]
- Forecast-calc parameters: revised PDP8 Decision 768 commercial electricity 500.4 to 557.8 TWh by 2030 with GDP near 10 percent per year 2026-2030; MONRE grid EF series 0.7221 (2021), 0.6766 (2022), 0.6592 (2023); heavy industry is capacity-driven with Hoa Phat Hai Duong 2.5 Mt per year BF-BOF, cement near 122 Mt capacity at 70-75 percent utilisation, clinker cap 65 percent; Hai Phong KH 4729 adds LNG 4800 MW, offshore wind 7200 MW, solar 4021 MW, and waste-to-energy 90 MW by 2030 to 2035 [Task 18]
- Blocked-source recovery map: B05 and B06 IGES file paths 403 even in-browser, working mirrors live under iges.or.jp/en/publication_documents (13020 Da Nang CAP 2nd ed 5.6MB, 6495 Low-carbon City Profile 6.39MB); C09 Decision 1266 official PDF at datafiles.chinhphu.vn/cpp/files/vbpq/2024/01/1266-ttg.pdf; C02 thuvienphapluat recovered by loading in a real browser until the challenge clears and saving page content; C13 ScienceDirect open-access via the pdfft View-PDF link, waiting 12-14s for redirect to pdf.sciencedirectassets.com, then fetching the signed URL from the article origin (8.9MB) [Task 19]
- gws on Windows: PowerShell mangles --params JSON quoting, so drive calls through Python subprocess invoking the run.js entrypoint with --params and --json as separate argv strings plus supportsAllDrives true on every call; gws --output rejects absolute paths, so run with workdir set and a relative output name [Task 19]
- Drive IDs for the BAU pack: Emission Reduction parent 1Qovv0Ngt8L8uepIts3DIROwg_JxANfpe, pack folder 1vAJetO0IJHwOeKHEn8v9SQ8W9kBg0Ayk, Sources subfolder 1AjlBouOl_vgnipeF3a6uEvVKQbeqgF3d; pack root holds evidence HTML plus sources_index.csv plus 3 lane briefs; Sources count (50) must equal index rows minus B14; final mandatory line is the herdr agent prompt w2A:p3 bau-upload DONE report as the LAST action [Task 19]
- File validation before upload: BAD if under 1000 bytes, containing Just a moment, cf-chl, or Attention Required, or a 181-byte chrome-extension pdf_embed stub; good PDFs start with percent-PDF magic (bytes 25 50 44 46); baochinhphu.vn HTML saved as gzip bytes (magic 1F 8B) needs gzip decompress first [Task 19]
- Hybrid standards verdicts for Trang 1A2 v1 (1959 firms baseline 8,118,819 tCO2e plus group-C add-on 528,894 equals 8,647,712 tCO2e, groups A38/A214/B72/B20/C100/D21, GWP 28/265): Q1 supported with conditions (2019R V1 Ch2 Eq2.3 residual x EFs-FRD plus EFas; GPC Eq5.2 fn15 scaling representative sample; GPC Ch6 I.3); Q2 10pt coverage floor unsupported and arbitrary; Q3 partly (keep measured floor, disclose remainder NE with notation key); Q4 partly (GPC intensity-per-output allowed as surrogate only with 3 IPCC steps plus stratification); Q5 AR5 28/265 required (Decision 18/CMA.1 para37, AR5 Table 8.A.1, BUR3/NIR2016, Decree06 defers to IPCC), AR4 contradicted; Q6 supported (MPGs para36 should-compare, V2 Ch6 good-practice upper bound near 5pt, Ch2 Table2.17 5pt-plus investigate). EU ETS 20MW and Vietnam BTR1 marked UNVERIFIED. [Task 20]
- SCATTER verdict 2026-10-09: no retrievable publisher workbook exists; scattercities.com is a dead parked domain (HTTP 200 body Site ready, headed-browser title Site ready, screenshot kept), Anthesis offers no self-serve download (old URLs 404, Cities page 0 scatter mentions), C40 hub sits behind LOGIN/REGISTER, Wayback holds only homepage shell plus methodology docs with zero .xls* site-wide and login-walled app paths. Method is UK-BEIS/LA calibrated, unfit for a merged Vietnamese heavy-industry province without full input override. [Task 21]
- GACMO v2.3 official files from https://unepccc.org/gacmo-tool/: gacmo-v2-3.xlsm 7703581 bytes SHA256 82FE4DA563ACD04E872B2B3D3BCCC20B56B3558855E87AB61CAC6F30080AEFBC (Last-Modified 10 Oct 2025), guidance docx and FAQ pdf with recorded SHAs; no login; free use, no commercial use without UNEP-CCC; vendor/ gitignored via tool-comparison/*/vendor/; 43 sheets with workflow Assumptions->Energy->GHG->Growth->BAU and AR5 GWP CH4 28 N2O 265 matching Decree 06. [Task 22]
- GACMO engine mechanics: BAU GHG holds ONE year-block driven by Growth col J cum-pct; stage each year by copying target cum col VALUES into J then recalc, saving/restoring J formulas and healing the K-depends-on-J chain each time; BAU GHG fuel rows shift +1 vs Energy (road 32 nav 35 households 36 services 37 agri 38); BAU power path returns 0 so 1A1 projection plus Scope2 are exact labelled post-processes (start-year power 20023.78 kt, implied coal EF 94.585 kg/GJ); run Excel 16.0 COM with AutomationSecurity=3 macros disabled; cast every Value2 write with [double] since JSON Decimals fail COM. [Task 22]
- GACMO headlines territorial Mt: RunA Hang 39.93/57.07/65.07/79.01/104.37/151.90 for 2025-2050; RunB corrected central 38.75/41.87/44.13/47.01/50.67/55.33, low 37.23/39.79, high 39.41/43.51; like-for-like tool effect on Hang boundary -1.2pct (A 63.96 vs 64.72 Mt 2030) with the +19Mt 1A2 scope line separate; B-vs-A -14.6Mt (-25.6pct) dominated by 1A2. Corrected anchors: 1A1 20.7, 1A2 9.4, 2C1 BF-BOF 3.65, Scope2 11.5 Mt; territorial about 40.7 Mt, BASIC+ about 31.5 Mt. [Task 22]
- Top-down cross-check 2026-10-09 for merged 2025: EDGAR TOTALS 42.11 Mt CO2 (HP 18.26 HD 23.86), Climate TRACE 28.46 Mt CO2e (HP 11.16 HD 17.29), EDGAR CO2e 48.96 Mt (42.11 plus 5.63 CH4 plus 1.22 N2O); Trang real about 11.67 Mt vs top-down 28.5-42.1 Mt with the power hole largest; 1A2 agrees -3pct; cement -65pct, waste -62pct. EDGAR CO2 grids are CO2-only; CH4 tonnes x28 and N2O tonnes x265 AR5; EDGAR 0.1deg leakage of about 2-4 Mt Quang Ninh coal makes EDGAR an upper bound; all sources CC BY, no login. [Task 23]
- Top-down source picks: Climate TRACE primary plus EDGAR secondary (city plus gridded); EDGAR UCDB 2026 xlsx 36.7MB holds Hai Phong city 11.76 Mt CO2e AR5 2024; Climate TRACE bbox 106.05,20.45,107.25,21.45 matched facilities (Hai Phong TPP 6.59M, Hai Duong TPP 6.2M, Pha Lai 5.93M, Hoa Phat steel 2.9M); use /v6/assets with year param, never /v6/country/emissions (returns identical values across years); use gbHumanitarian boundary (matches GADM under 0.1pct), never gbOpen 2008. [Task 23]
- LEAP licensing facts: LEAP 26.7.3 evaluation lock is licence state with saving disabled; free licences only for qualifying non-profit/academic/gov in low/lower-middle-income countries, so private Allotrope does not qualify while a Vietnam beneficiary (Haiphong gov/university/NGO) could qualify in its own name; Evaluation Terms forbid research/analysis/consulting/teaching use; SEI denied Allotrope on 2026-10-09 (private org needs a Standard licence); build_leap_bau.py is ready (--check passes) for once a licence is active; BAU stands without LEAP on GACMO Run B. [Task 24]
- LEAP acquire-map facts 2026-10-09: download at https://leap.sei.org/download is members-only behind signup plus separate software licence application with 24h verify; acquired vendor/setup64.exe 205788736 bytes SHA256 59595210D829A24C871D388984944F44A24F4FECD80C52CCDEEA8AA07FD3BF68 ProductVersion 26.7.3, Authenticode Valid signer CN=Stockholm Environment Institute US via Sectigo R36, installed to C:/Program Files/LEAP; inputs.csv 67 rows with central drivers pop 0.8pct, steel 2.5Mt cap, clinker 10.18Mt capacity x 72.5pct utilisation = 7.38Mt, elec 10pct, grid 0.6592 to 0.55 with no x1.15, territorial 40.7Mt vs BASIC+ 31.5Mt. [Task 25]
- LEAP COM automation facts: ProgID LEAP.LEAPApplication registered with TLB at C:/Program Files/LEAP/Leap.tlb; AddTechnology needs 6 args, AddCategory 4, AddProcess 4, AddModule 13; call ShowAnalysisView before area calls and iterate COM collections with Count plus 1-indexed Item(k); authoritative areas path is the OneDrive Documents LEAP Areas folder; evaluation-mode save lock makes Areas.Add hang or no-op with StaticData closed-dataset errors. [Task 25]
- IPCC Tier-1 cross-check verdicts 2026-10-09: tool total 15.30Mt as-sent / 15.88Mt corrected; 1A2 placeholder 12.79Mt (+47.9pct vs hybrid v4 8.65Mt with steel 4.73Mt); cement -0.9pct Trang EF sound, lime -0.4pct correct, steel EF wrong route (-95.9pct vs BOF 1.46); Energy 1A1/1A3/1A4 unpopulated; GWP AR5 consistent; engine IPCC Inventory Software v2.98 plus 2006GL/2019 Refinement plus EFDB, 7 files from ipcc-nggip.iges.or.jp with recorded SHAs, manual has no CLI so engine blocked-not-installed. [Task 26]
- CIRIS 2.6 cross-check verdicts 2026-10-09: CIRIS ships no default EFs and computes amount x converter x EF looked up by identifier with Report SUMIFS on A=T into Results_Overview then Results_Summary C12; Trang PV1 grand total 15300606.2 t omits whole AFOLU 564368.5 t; CIRIS BASIC+ IPPU 1979234.364 plus AFOLU 564368.5 plus Waste 476595.7 = 3020198.6 t matches Trang to the tonne; 1A2 in-scope 483 firms (358 Baseline+ plus 125 Baseline-) with 9 fuels 87635.8TJ = 8118818.5 t, LPG kg-as-tonnes slip at NL(pivot) M1501 worth -273086 t, lpgfix 8374626.48 t equals EDGAR 8.37M. [Task 27]
- AFOLU-Waste cross-check verdicts 2026-10-09: AFOLU true 564368.56 tCO2e reported as 0 (missing sector totals) with waste 476603.55 t and corrected total 15881260 vs reported 15300606; reproduction exact for enteric 29174.60, manure CH4 18350.84/N2O 7053.79, rice 605682.16, landfill 3226.599775 t CH4; gaps over 10pct are rice -44.9pct (VN Tier2 vs IPCC EFc 1.30), manure CH4 +30.7pct (Tier1 vs Tier2 swine), enteric -15.7pct, landfill -12pct (DOCf 0.5 vs 0.7/0.1, garden k 0.03 vs 0.17); primary is IPCC 2006 Vol4/Vol5 worksheets plus Waste FOD Model with 15 files direct from ipcc-nggip.iges.or.jp. [Task 28]
- Drive flat-upload pattern repeated across four lanes 2026-10-09: upload .md/.csv/.py/.ps1 plus own run/output workbooks with flat basenames, EXCLUDE vendor/.venv/.work/__pycache__/temp and files over 50MB, never create folders shares or deletes, verify Drive listing names plus sizes vs local, write UPLOAD.md with name plus Drive id plus bytes, then ONE herdr DRIVE line with no --wait; ipcc 17 files 0.58MB, ciris 72 files 10.2MiB, afolu-waste 26 files 1.11MB, topdown 12 files. [Task 23][Task 26][Task 27][Task 28]
- Related skill: skills/gws-drive-flat-upload/SKILL.md
- gws Drive-upload pattern that worked: PowerShell mangles --params JSON, so ship one file per cmd /c call from batch .cmd files with escaped JSON and CRLF line endings; list with quoted-id in-parents and trashed=false; never let case-colliding vars share scope. [Task 23]
- 10pt-cutoff source search result: 0 DIRECT sources for a fixed coverage floor; 9 ANALOGOUS 10pt-family thresholds (EU MRR Art19(3) minor below 10pt and de minimis below 2pt; GPC Ch11 CCAR 10pt recalc with GPC making no recommendation; Circular 17 Art22 above 10pt recalc; Decree06 10pt offset cap; MPGs 0.05pt/500kt with total below 0.1pt; GHG Protocol draft 1pt/1pt/5pt; Census ACS 70pt/30ptCV; (n,k) dominance; weight trim cap 5). Method-note wording: state 10pt as documented internal screening rule analogous to, not derived from, those thresholds, with sensitivity sweep 0/5/10/25pt. [Task 20]
- Threshold recomputation on data/incoming/2026-10-08_trang_1A2_v4/hybrid_rows_extract.csv (245 rows) in scripts/scratch_threshold/ (explore_hybrid.py, rules.py, rules2.py, n_check.py, wb_check.py, fix_viet.py): coverage at or above 10pt equals expansion factor at or below 10x; Hidiroglou-Berthelot U=0 A=0.05 C=3 on city/sample ratio flags exactly 21 D rows for add-on 528894 tCO2e (+0.0pt); stability band below 1pt for 7.5-12.5pt and below 10pt for 1-30pt; national-ceiling alone plus 11pt (7 breaches, bricks 164pt, packaging 17198pt) needs unity edit to reach finish line; n at or above 10 kills add-on (median 2 firms). Finish line 8.65Mt as sent, 8.10Mt after LPG -0.27Mt plus billet -0.28Mt fixes; validated cell-for-cell against workbook sheet 'Phan tich nguong'. [Task 20]
- Primary-PDF quote workflow that held for IPCC/GPC briefs: curl 11 PDFs from ipcc-nggip.iges.or.jp, ghgprotocol.org, unfccc.int into %TEMP%\hp1a2src, text-extract with pdftotext.exe -layout, then srch.py/dump.py searches keeping printed-vs-PDF page distinction for verbatim quotes. [Task 20]

## Failures and how to do differently

- Reconcile analytics with raw workbook rows before claims; use `PYTHONIOENCODING=utf-8` for Vietnamese output. Artifact sharing may expose tax codes/firm identifiers: check and warn/remove before publishing. [Task 1][Task 2]
- Do not present the 913,542 tCO2e eight-park figure and derived electricity Scope 2 as directly comparable; boundaries differ. Do not claim late background-agent research without completion evidence. [Task 4]
- In PowerShell, use `Select-Object -First N`, not Unix `head`. When pre-commit pytest outlives an initial command wait, poll the running session before retrying or declaring the commit failed. [Task 5]
- PowerShell on this host has no `head`, `wc`, or multi-path `ls`; use Get-Content -First / -Tail and one Get-ChildItem/Get-Content per call, and strip HTML in JS via regex. [Task 6][Task 7]
- `apply_patch` with `*** Add File:` plus raw markdown or bare `@@` hunks fails verification; write large markdown via base64 chunks (utf8 bytes plus b64 in JS store, then [IO.File]::WriteAllText for chunk one and AppendAllText after, about 8k b64 per exec_command) and verify with (Get-Item).Length plus Get-Content -First / -Tail. Probe tiny patches first with exact `*** Add File:` / `*** Update File:` plus `@@` plus `+`-prefixed lines. [Task 6][Task 7]
- Direct `uv run python -c` with quoted workbook paths fails under this exec wrapper (PowerShell plus nested-quote parsing, leading-zero and Buffer errors); write python to $env:TEMP via base64 then `uv run python` with yield_time_ms 60-120s plus wait/write_stdin polling, and filter the openpyxl extension warning. Prefer file-based .py helpers written via apply_patch over inline python. [Task 7][Task 8]
- UNFCCC, nature/science, and several NSO pages block bulk fetch (Incapsula/403/client-challenge); list them as blocked and rely on verified PMC and open copies with a note. IPCC 2019 Refinement needs correct Ch paths discovered via vol index link listing; the GPC full PDF works via standards/GPC_Full_MASTER_RW_v7.pdf. [Task 8]
- PowerShell gws with unescaped parentheses returns 400 validationError -> use Bash with single-quoted JSON params; gws gmail get metadata parsing can fail KeyError headers -> pivot to Gmail get_message MINIMUM/PLAIN_TEXT; Bash heredoc cat of large HTML fails unexpected EOF on single quotes -> use the Write tool. [Task 9]
- Full-tree ruff fails on untracked scratch so scope ruff to tracked paths for the gate; a commit hung on pre-commit hooks proceeded after an empty write_stdin; uv sync wrapper errors can be ignored when pytest itself passes. [Task 10]
- Dispatch goal text contained the unexpanded placeholder briefs${f}.md across parallel sessions, so several r-* agents duplicated lanes; self-identify the lane from live herdr agent state (agent list plus visible pane buffer, not WMI ancestry) and flag unowned lanes to city-claude rather than stalling. [Task 12]
- apply_patch writes can appear to succeed while a sibling worker overwrites the same shared file; on parallel brief runs re-list and cat-verify before claiming authorship and prefer verify-and-keep over overwrite. apply_patch fails if the patch does not end with *** End Patch. [Task 11]
- PowerShell mangles inline $variable assignment and leading =/quotes in exec strings, and glob ls -l research/2026-10-06_hp-1A2-*.md throws PathNotFound; use the workdir param with simple commands (dir research, Get-ChildItem) and filter instead of globbing. [Task 11]
- Firecrawl 402 out of credits plus Bing/DDG/Mojeek/Startpage/Ecosia HTML blocked or JS-only plus thongkehaiphong anti-bot means general search is unusable for city-ghg lanes; pivot to enumerable official endpoints plus Wayback CDX. Signed image-only PDFs (QD13 signed 181pp) with no OCR available means use Cong Bao text PDFs plus luatvietnam HTML instead. [Task 13]
- PDF text-layer row-splitting breaks STT parsing and TOE regex misses EVN rows (233 versus 248); fix with an STT-anchored parser checking SCT/EVN anchor plus fallback last-number pattern and verify the 248-row sum. A bad fix script truncated the brief, so rebuild from stored b64 chunks and guard overwrites with size asserts (over 90k). [Task 13]
- tools.web_search does not exist in this harness; enumerate ALL_TOOLS and use mcp__codex_apps__search_service_web_run. PowerShell Set-Content adds UTF-8 BOM that breaks json.load, so open with utf-8-sig; Windows stdout UnicodeEncodeError needs sys.stdout.reconfigure(encoding=utf-8, errors=replace). Direct PDF 404s are common (superseded or moved files), so log honestly and use full-text copies or superseding versions; scanned PDFs with no extractable text (Halifax HRM 2008) are opened-but-not-quotable, never invented. [Task 14]
- Firecrawl search returning empty then 402 out-of-credits is a routing cue, not a stall: pivot to curl plus pdftotext and direct PDF opens, OpenAlex API for discovery, Wayback CDX id_ for UNFCCC and IGES PDFs, and r.jina.ai reader for Cloudflare 403 and 406 pages; never cite unopened sources or invent URLs [Task 16][Task 17]
- archive.org wayback availability API 429s under load while direct CDX queries still work, so use CDX directly; lite.duckduckgo returns a bot-challenge iframe, so do not rely on general search [Task 17]
- baochinhphu.vn returns compressed bytes via urllib, so fetch with curl --compressed then strip with a gzip-aware script and grep raw bytes when txt stripping mangles Vietnamese diacritics; base env has no pypdf or pdfplumber, so use uv run with pypdf [Task 18]
- browser-control relay EADDRINUSE on 127.0.0.1:19989 means the relay is already running, so reuse the session via status --json instead of restarting; browser-control download events are unsupported, so fetch bytes in-page and write with fs and path sandbox modules [Task 19]
- EUR-Lex PDF curl returned 0 bytes; the Art19(3) minor below 10pt and de minimis below 2pt quotes came from the HTML scrape instead, so prefer the EUR-Lex HTML view over the PDF for MRR articles. ISO14064-1 PDF was not text-extractable (57-byte txt), so mark it UNVERIFIED rather than forcing a citation. [Task 20]
- df.cov shadows the DataFrame.cov method and throws TypeError, so rename coverage columns to covr; printf-style comma formatting fails, so use f-string {TRANG:,.0f}. The first HB formula used a simplified MAD version; the correct edit interval is true HB s_i/E_i with U, A=0.05, and C sweep after reading the rendered scan images. Vietnamese output crashes cp1252, so set sys.stdout.reconfigure utf-8 and write ASCII-safe first, then run a full-diacritic replacement pass (fix_viet.py) verified by a diacritic check script. [Task 20]
- Inline pypdf probing failed on quoting, so write probe.py via PowerShell here-string and run python on the file. apply_patch fails when the patch contains triple-backtick fences or raw Unicode, so rewrite ASCII-safe first and patch diacritics in a second pass. [Task 20]
- chrome-devtools-axi sessions lose pages (No page is currently selected, pages=[about:blank]); chain newpage plus screenshot in one exec call under CHROME_DEVTOOLS_AXI_SESSION plus CHROME_DEVTOOLS_AXI_HEADED=1, and prefer selectpage plus eval innerText over snapshot on heavy pages. [Task 21]
- Wayback CDX filtered original-regex queries can return empty while unfiltered domain samples work; test connectivity first, then fall back to homepage archive link extraction plus uploads/pages prefix queries; time-box publisher-only Wayback sweeps to 20 min. [Task 21]
- Downloaded xlsm copies carry Mark-of-the-Web Protected View that breaks COM writes with InvalidCast; run Unblock-File on every copy before Workbooks.Open, kill orphan EXCEL.EXE before retry, and guard staged row counts before appending post-process rows. [Task 22]
- PowerShell ConvertFrom-Json returns Decimals that fail COM Value2 writes and results.csv carries a BOM that breaks csv DictReader; cast [double] on every write and open results with utf-8-sig. [Task 22]
- openpyxl stalls on 36MB workbooks under default 30s yields; unzip the xlsx via tar and parse sheet xml/sharedStrings with chunked scripts and background session polling. [Task 23]
- GADM NAME_1 strips spaces (HaiPhong/HaiDuong) so naive PIP matches zero; check shapeName plus space-stripped keys, add a bbox pre-filter fast-path, and use geoBoundaries gbHumanitarian over gbOpen 2008. [Task 23]
- Bulk Remove-Item is policy-blocked while single-file deletes succeed; delete session outputs one by one and verify with a final Get-ChildItem plus git status. [Task 24]
- LEAP COM failure shields: do not call leap.Visible=False plus ShowSplash=False blindly since it stacks blocking dialogs; keep Visible True for diagnosis and dismiss stacked OK dialogs via BM_CLICK; do not retry/kill/relaunch when told to hold; kill hung python helpers before re-probing; pipe-delimited branch columns break CSV parsing so split into run/branch/parameter and validate no empty territory/status. [Task 25]
- CIRIS Excel-COM failure shields: full-workbook CalculateFull hangs (69s+ frozen) so delete heavy sheets (Results_Graphs_2, Notes, eCRF) and calculate only Emission factors, F-Gases, IV, V, III, Report, Results_Overview, Results_Summary, Results, GCoM-CRF; never call Worksheet.Unprotect since it prompts for password and blocks COM, use Validation.Delete only; Add-rows carry pre-filled M=NO that short-circuits VLOOKUP roll-up to NO/0 so clear M14 (IPPU) and M14/M71/M128 (AFOLU) before recalc; BASIC+ set in City E44 does not propagate so set Results_Summary C12 directly. [Task 27]
- Wrong-workbook shield for inventory lanes: the early template hp/hph-survey-data-2026-09 file holds Energy plus IPPU only with 1000 placeholders, so diff the candidate against the primary plus TAH review before mapping; any cell exactly 1000 is not-yet-populated and must never be compared. [Task 26][Task 27][Task 28]
- gws upload failure shields: PowerShell direct --params/--json quoting always yields invalid JSON, so drive gws from Python subprocess calling node run.js (ipcc) or from Git Bash scripts (ciris upload.sh); a double-launched uploader created 50 files for 25 unique, so ensure a single uploader instance and reconcile by keeping earliest createdTime and trashing duplicates. [Task 26][Task 27][Task 28]

# Task Group: VIDA/CPI model review and investor materials
scope: Review VIDA scale-up economics and slide/vehicle materials without silently overwriting team-owned Drive models.
applies_to: cwd=C:\Users\tukum\Downloads\remote\cpi; reuse_rule=workbook-version-specific; reproduce against exact workbook/column before using figures

## Task 1: VIDA incubation dispute triage plus Mudit v3 scale-up model review and edit register, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-z1TE-vida_scaleup_whatsapp_mudit_model_review.md (cwd=C:\Users\tukum\Downloads\remote\cpi, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-adb0-75c0-b781-326a16841df6.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-adb0-75c0-b781-326a16841df6, 8 tasks: WhatsApp triage, v3 model review, version compare, reply drafts, targets/sensitivity, HTML review plus Excel prompt, manual register; read-only review plus separate register)

### keywords

- VIDA_Model_v3_15Sep26.xlsx, Drive edits for Mudit, failure recovery, commercial hurdle, waterfall, 1.25x, WhatsApp javascript_tool extraction, levers.py, 10pct 2-5pct targets, conc pref 1.12x, opex 150k, 2026-09-18_vida-model-v3-improvement-review.html

## Task 2: Vehicle overview tracked redline, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-40-9Gi9-vida_vehicle_overview_tracked_redline.md (cwd=C:\Users\tukum\Downloads\remote\cpi, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-40-01a0e1d3-aa0c-7703-84ad-57095754a3f5.jsonl, updated_at=2026-09-27T07:45:40+00:00, thread_id=01a0e1d3-aa0c-7703-84ad-57095754a3f5, tracked redline with 62/62 tests green plus LibreOffice PDF render; source SHA unchanged)

### keywords

- VIDA Vehicle Overview, tracked changes, redline, CPI, investment thesis, w:sdt, commentsExtended paraIdParent, unslop, redline ledger, 194000 tCO2e, 294000 MWh, 1870 job-years

## Task 3: Final VIDA slides/calculation review, uncertain

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-jQ1v-vida_slides_calc_final_review.md (cwd=C:\Users\tukum\Downloads\remote\ceba, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a7f8-71b2-bb17-0fa169f86d15.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a7f8-71b2-bb17-0fa169f86d15, pre-send issues identified)

### keywords

- VIDA slides, calculation workbook, pre-send review, concessional IRR, GP carry

## User preferences

- after “Too long man” then “too short without any context behind number” -> be compact but place numerical rationale beside each recommendation [Task 1]
- “exact sheet and cell and what exactly i need to change or comment for mudit to update” -> give exact locations and paste-ready comments; inspect/recommend before edits and preserve Mudit’s Drive source [Task 1]
- when reviewing a draft with pending teammate edits, the user expectation is to preserve them intact and redline over them visibly rather than silently replacing -> Rob 21 Sep and Lauren 18 Sep edits preserved; R-06 redlines over Rob callout rewrite [Task 2]
- when numbers are uncertain, the user wants flags as comments not silent decisions -> impact confirmation, 49M denominator, 120MWp/40MWh mismatch left as comments [Task 2]

## Reusable knowledge

- Base v3 scale-up reproduces near 4.9% fund, 14.1% commercial, -1.2% concessional and no GP economics because the $3.55M 1.25x commercial preference exceeds roughly $2.69M net profit. [Task 1]
- The manual edit register has 22 rows and retains original tabs/formulas in a separate Tung workbook. Ask Mudit to restore live sensitivity formulas/tables, which Drive copy flattened. [Task 1]
- WhatsApp triage verdict: <SUPERVISOR> right that fee too low ($260k/yr near 1.06% under 2% for 35 projects), wrong that fee plus opex cannot coexist (investor view counts both as fund costs) and wrong venue/tone pre-endorsement; Joyce 2%-then-1.5% lacked method; Rob 4% combined ask models worse (conc 0.92x). Ground chat interpretation in most-recent Drive/local files, never chat alone; prefer javascript_tool extraction of #main [data-pre-plain-text] over screenshots for WhatsApp. [Task 1]
- Mudit v3 email supersedes Joyce WhatsApp numbers: 2% fee ($1.946M), $300k/yr opex, all-in near 2.8%/yr; v3 bugs are $300k opex copied from pilot (double-count), steep 1.25x hurdle, start-year from fund-life cells, exit-timed recovery, no delay room. Working fix direction is opex near $150k plus hurdle 1.12-1.20x keeping 2%, with internal targets commercial 12-15% (13%), concessional 5-6% floor 4%, fund near 9-10%. [Task 1]
- Only 2 manual values for the Drive file: Assumptions D9 300->150 and Results and Levers D14 1.25->1.16 plus Change Log B3 note, with 10 structural comments; check values are 6.4%/11.6%/1.3%/1.47x and full fix reaches 10.1%/2.2%/1.27x. Recalc via LibreOffice headless after openpyxl edits. [Task 1]
- Vehicle Overview governing figures for the one-pager: 194,000 tCO2e plus 294,000 MWh plus near 1,870 job-years at full 24.5M scale; pilot is $4.9M fund plus $1.5M grant = $6.4M near 14 projects near $350k ticket; scale-up ticket near $700k with sizing near 5MWp pilot / near 10MWp scale-up; grant covers setup plus opex; say de-risking support not services; describe KBC ties as allude-only not partnership. [Task 2]
- OOXML pitfalls in this source family: prose lives inside w:sdt content controls so run walkers must recurse through sdt/sdtContent, smartTag, ins/del; comments carry only w:commentRangeStart (9 ids, no RangeEnd/Reference) so thread replies via commentsExtended paraIdParent; the source already ships a commentsExtended part so use ensure-guards on override/relationship; revision ids 0/2 already collide in-source so seed new ids from max. Proven workflow is ledger-driven script reusing apply_vida_preseed_review.py primitives plus tracked-row insert, test-first with 62 checks, accept-all preview, LibreOffice PDF render plus python-docx open validation, source SHA unchanged. [Task 2]

## Failures and how to do differently

- Failure recovery at Stage Gate C18 is budget never spent/avoided cost, not contractual repayment: reduce deployment/capital calls rather than booking same-year proceeds or spreading it as repayment. Reproduce every stakeholder IRR in the exact workbook and column. [Task 1]
- Treat proposed opex as an operating-budget fact requiring agreement, not an IRR tuning dial. [Task 1]

# Task Group: Gap clean-energy financing, suppliers, and timeline operations
scope: Produce decision-ready Gap financing/timeline artifacts and maintain supplier evidence without overstating inferred mappings.
applies_to: cwd=C:\Users\tukum\Downloads\ee-heat; reuse_rule=project-specific; verify live Drive/workbook state and audience before delivery

## Task 1: Financing scenarios deck and supplier workbook update, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-38-Y81P-gap_financing_deck_and_supplier_v2.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-38-01a0e1d3-a2c9-7f00-8c1e-08908b214c81.jsonl, updated_at=2026-09-27T07:45:38+00:00, thread_id=01a0e1d3-a2c9-7f00-8c1e-08908b214c81, 10-slide visual deck plus v2 workbook with 5 suppliers; Milestone 2 scope captured)

### keywords

- gap-financing-scenarios-2026-09-25.html, combined Allotrope Suppliers_09_025_2026 v2.xlsx, xlwings, Higg ID

## Task 2: Cong timeline tracker and Drive upload, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-6BxG-gap_timeline_tracker_cong_tech_lead.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a5e2-76a0-997c-8a96fdbf178c.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a5e2-76a0-997c-8a96fdbf178c, tracker uploaded)

### keywords

- Cong, technical lead, timeline tracker, Drive, clean energy, Gap

## Task 3: Gap supplier calendar guest-list aggregation and analysis, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-vlJ1-gap_supplier_calendar_guest_analysis.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-ad98-7ea1-ac25-7f6f21e9d4a3.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-ad98-7ea1-ac25-7f6f21e9d4a3, 141 invitees aggregated with RSVP/coverage-gap findings; domain mapping partly inferred)

### keywords

- fdm_rollup.json, 23 priority facilities, 141 invitees, PT Leetex zero seats, Hantex 1 seat, coal cohort, guest list, calendar-search, domain-aggregation, coverage-gap, role mailboxes, free-mail

## Task 4: Gap supplier webinar deck v1 to v5 on team template, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-GWMv-gap_supplier_webinar_deck_v1_to_v5.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b6bb-7be2-bc96-540e1a26c927.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b6bb-7be2-bc96-540e1a26c927, kickoff-recycle constraint with Drive transfer workflow)

### keywords

- Gap, supplier webinar, kickoff v7, team template, Rob Hardison, Lauren, SmartArt hidden, gws drive download, pptx build, pytest deck

## User preferences

- “html presentation artifact,” “less word more visual and animation,” and “clarify with me where needed” -> use visual storytelling and confirm scenario/audience assumptions before building [Task 1]
- when asked to check a call note and brainstorm, the user accepted structured AskUserQuestion narrowing (core job, objection, lead benefit, storyline) and answered quickly, including rewind and multi-select -> for similar deck scoping, use short option questions to lock decisions rather than long prose [Task 4]
- when brainstorm was done, the user said skip plan and execute the deck based on brainstorm -> on explicit skip-plan plus execute, build directly without a plan step [Task 4]

## Reusable knowledge

- Preserve existing workbook charts by using Excel/xlwings for row append; match columns by header and verify endpoint rows/Higg IDs/chart parts after saving. [Task 1]
- Gap CSA Milestone 2 is the financing assessment with deliverable Financing options and structuring report due December 2026 covering pathways plus SWOT plus Gap role plus risk mitigation; Stage 2/3 need an executed amendment. Tung owns EE plus clean heat only; on-site solar, BESS, and off-site DPPA sit with Rob Hardison. [Task 1]
- The 23-facility scope in `pipeline/gap_data/fdm_rollup.json` (dict keys suppliers/y2025/y2026/supplier_ids, suppliers keyed by Higg ID) matches `Allotrope Suppliers`; the Wed 23 Sep 10:00-11:00 (+07) call organized by <EMAIL> drew 141 invitees = 129 supplier-side plus 7 Gap plus 5 Allotrope with 0 supplier RSVPs (all optional needsAction, guestsCanInviteOthers=false). Coverage gaps: PT LEETEX (Presslink T1, 37% prod) zero seats; coal cohort 9/23 thinnest at GDI 100% coal/3 seats and Hantex 99.2% coal/70% prod/1 seat; 37 seats outside scoped 23; VN-facing 60 vs ID-facing 32 vs unresolvable 31; 20 role mailboxes plus 15 free-mail. Group-domain seat counts cannot split to facility; treat them as outreach hypotheses, not facility-certainty claims. [Task 3]
- Large Drive pptx (10.6MB) must be fetched via gws CLI (drive files get with alt media) not the connector, byte-verified 10632398. [Task 4]
- Template SmartArt carries internal wording; patch data*.xml plus drawing*.xml to supplier-facing text. Clone the template title+subtitle slide for new slides to match geometry; render via present skill render_deck.py (LibreOffice) and eyeball PNGs. [Task 4]
- v2 strayed too far from kickoff per Rob; rebuilt v3 to 73% kickoff provenance (8/11 content slides) enforced by test_kickoff_provenance. [Task 4]

## Failures and how to do differently

- Render/open published HTML and verify navigation before calling it ready. Domain-to-facility mappings, especially shared domains, are estimates; label seat counts at domain level. Write large quoted scripts to files rather than fragile inline heredocs. [Task 1][Task 3]


# Task Group: CEBA Amazon RFP debrief email drafting and Gmail staging
scope: Draft an internal RFP debrief email from a call transcript and stage it as a Gmail draft via the gws CLI without sending.
applies_to: cwd=C:\Users\tukum\Downloads\remote\ceba\amazon; reuse_rule=account-sensitive (<EMAIL> default config); recheck auth config and recipient mapping before staging

## Task 1: Draft Kait RFP debrief email from transcript, success

### rollout_summary_files

- rollout_summaries/2026-10-01T08-58-35-UGZl-kait_rfp_debrief_email_gws_draft.md (cwd=C:\Users\tukum\Downloads\remote\ceba\amazon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\01\rollout-2026-10-01T15-58-35-01a0f6af-db14-7523-abd1-0417bc671113.jsonl, updated_at=2026-10-01T10:14:05+00:00, thread_id=01a0f6af-db14-7523-abd1-0417bc671113, local draft plus Gmail draft staged, not sent)

### keywords

- gws, gmail drafts create, <EMAIL>, Kait Payne, Amazon CFE RFP, allotropevc addresses, Fair Market RFP, debrief email

## Task 2: Create Gmail draft via gws CLI, success

### rollout_summary_files

- rollout_summaries/2026-10-01T08-58-35-UGZl-kait_rfp_debrief_email_gws_draft.md (cwd=C:\Users\tukum\Downloads\remote\ceba\amazon, rollout_path=C:\Users\tukum\.codex\sessions\2026\10\01\rollout-2026-10-01T15-58-35-01a0f6af-db14-7523-abd1-0417bc671113.jsonl, updated_at=2026-10-01T10:14:05+00:00, thread_id=01a0f6af-db14-7523-abd1-0417bc671113, draft id r7920195608511911175)

### keywords

- gws gmail users drafts create, userId me, base64url EmailMessage, GOOGLE_WORKSPACE_CLI_CONFIG_DIR, default config auth, Python subprocess json.dumps

## User preferences

- when asked to draft an internal debrief, the user said use the transcript to draft a debrief email to named colleagues and "Do not send" -> default to a local paste-ready file first and never send without an explicit send instruction [Task 1]
- when only a local draft existed, the user asked "can you use gws cli" -> attempt live Gmail staging via gws rather than stopping at a local .md [Task 2]
- when the agent started a `gws auth login` flow, the user corrected "gws should already be auth" -> check default `~/.config/gws` auth status and getProfile before starting any login flow [Task 2]

## Reusable knowledge

- Source transcript is `Kait RFP call Oct 1 2026.md` and prep context is `amazon-cfe-rfp-call-prep.html` in `ceba/amazon`; key RFP facts: 3 electronics suppliers, 5 milestone phases, Fair Market issue by Fri 2 Oct, questions due 12 Oct, bid due 26 Oct, $700k too much, CEBA cohort ask too big. Local draft artifact is `Kait RFP debrief email draft.md` in `ceba/amazon`. [Task 1]
- gws authenticated credentials live in default `~/.config/gws` (oauth2 as <EMAIL>), NOT `~/.config/gws-work` or `~/.config/gws-personal` which return 401 No credentials; unset or pop `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` to use the default. [Task 2]
- gws `--params` JSON quoting fails in PowerShell; the reliable pattern is Python subprocess with `json.dumps({"userId":"me",...})` and `encoding="utf-8", errors="replace"` plus `$env:PYTHONIOENCODING='utf-8'`. Gmail draft create requires both params and body: `gws gmail users drafts create --params '{"userId":"me"}' --json '{"message":{"raw":"<base64url EmailMessage>"}}'`; omitting userId gives 400 Required path parameter userId is missing. [Task 2]
- Resolved recipients from Gmail history (@allotropevc.com): mmr (<FINANCE_CONTACT> Murphy Rogers), jrh (Rob Hardison), chn (Cong Nguyen), hal (Hong Anh Le), lem (Lauren McGinley); "Anh" mapped to Hong Anh Le with an open check. [Task 2]

## Failures and how to do differently

- The agent wasted turns trying `gws-work`/`gws-personal` configs and launching interactive `gws auth login` (TTY scope picker hung, had to kill node/cmd processes); next time run default-config `auth status` plus `gmail users getProfile --params {"userId":"me"}` first. [Task 2]
- Python Gmail harvest hung and hit cp1252 UnicodeDecodeError; fix with utf-8/errors=replace and redirect to file with a long wait. Cleanup of temp `_tmp_*.py` and `_login_out.txt` can lock (used by background process) and needs a process kill before delete. [Task 2]
- An initial draft header claimed work Gmail was not authenticated; verify auth in the default config before claiming unauthenticated. [Task 1][Task 2]

# Task Group: Gmail draft enrichment with LinkedIn and news links
scope: Enrich an existing Gmail draft inline with the user's own LinkedIn post links plus external news links for claims without a post; save drafts, never send.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=account-sensitive (<EMAIL> drafts); recheck draft id and recipient before editing

## Task 1: Add LinkedIn links to Allotrope update draft, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-qmcW-allotrope_draft_linkedin_bidv_pcaf_links.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b5b9-7a32-8cf3-4bc91acbec8a.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b5b9-7a32-8cf3-4bc91acbec8a, draft enriched and saved, not sent)

### keywords

- Gmail draft, LinkedIn activity, Allotrope update, BIDV PCAF, CEBA, Hai Phong decarbonization, Industrial Decarbonization Accelerator, claude-in-chrome, update_draft

## Task 2: Find external BIDV PCAF news link, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-qmcW-allotrope_draft_linkedin_bidv_pcaf_links.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b5b9-7a32-8cf3-4bc91acbec8a.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b5b9-7a32-8cf3-4bc91acbec8a, Bizhub article used for first-signatory claim)

### keywords

- BIDV PCAF, first Vietnamese bank, Bizhub vietnamnews, firecrawl search, external news link

## User preferences

- when email bullets were missing links, the user said get those links from posts on LinkedIn and integrate into email -> reuse the user's own LinkedIn posts as evidence links integrated inline in the existing draft, not rewriting wording [Task 1]
- when LinkedIn had no BIDV-PCAF post, the user said get a BIDV PCAF link elsewhere -> back the factual claim with an external credible news link even if it is not Allotrope-related [Task 2]

## Reusable knowledge

- Gmail draft found via Gmail list_drafts by subject (Allotrope update: id r-595153312126740829, to chi Trang, from <EMAIL>, 4 bullets); update via update_draft with htmlBody containing anchor tags; draft stays unsent. [Task 1]
- LinkedIn user is Tung Ho, Country Director at Allotrope Partners; the recent-activity page covers the bullets; feed URL shape is https://www.linkedin.com/feed/update/urn:li:activity/<id>/ with the 4 mapped activity ids in the rollout. [Task 1]
- BIDV became the first Vietnamese bank to join PCAF effective 14 May 2026 (reported 17 Jul 2026); the article used is the vietnamnews Bizhub piece confirming the first claim with no Allotrope mention; alternatives are VietnamPlus and VietnamNet English. [Task 2]

## Failures and how to do differently

- Large JS scraping of LinkedIn timed out (Runtime.evaluate 45s); small chunked javascript_exec queries (one post at a time, sliced innerText, qs-url filtering) worked; get_page_text returned minimal content, so rely on querySelector data-urn plus innerText. [Task 1]
- Initial firecrawl_search returned generic PCAF pages first; refined query around PCAF BIDV first Vietnam bank signatory 2026 surfaced direct BIDV sources. [Task 2]

# Task Group: CEBA policy-session decks and senior advisor deliverables
scope: Create concise, decision-ready client-facing policy decks and SOW documents with strict visual/length QA.
applies_to: cwd=C:\Users\tukum\Downloads\remote\ceba and cwd=C:\Users\tukum\Downloads\city-ghg; reuse_rule=deliverable-specific; verify current project status before reusing content

## Task 1: October CEBA policy deck build and unslop, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-qAH7-ceba_oct2026_policy_session_deck.md (cwd=C:\Users\tukum\Downloads\remote\ceba, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a58f-7b01-9633-7f6ef294ad61.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a58f-7b01-9633-7f6ef294ad61, deck QA completed)

### keywords

- CEBA, October 2026, policy session, unslop, deck, slides

## Task 2: Senior Decarbonization Advisor SOW two-page rewrite, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-38-WN9F-senior_advisor_sow_2page_rewrite.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-38-01a0e1d3-a2ba-75f3-936e-c724224da0ab.jsonl, updated_at=2026-09-27T07:45:38+00:00, thread_id=01a0e1d3-a2ba-75f3-936e-c724224da0ab, exactly two PDF pages)

### keywords

- Senior_Advisor_SOW_2026-09-25.docx, build_sow_2026-09-25.py, VEEP, python-docx, pdfinfo, pdftoppm, hp gitignored, ind stay dropped, Hai Phong, ViDA, Gap

## Task 3: CEBA EE deck v2.2 revision from <FINANCE_CONTACT>/Lauren feedback, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-oWdp-ceba_ee_v2_2_revision_and_unslop_sync.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b309-7450-af5f-330dfd204b57.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b309-7450-af5f-330dfd204b57, 7/7 tests green plus PDF QA 0 issues; committed 384ab92 and aa338fa and pushed)

### keywords

- CEBA EE deck v2.2, build_ee_pptx.py, test_ee_deck.py, Lauren McGinley, <FINANCE_CONTACT> Murphy Rogers, Drive silent edits, FLEX slides, speaker notes, header autofit

## Task 4: Interactive-exercises brainstorm meeting prep as HTML report, uncertain

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-lEpU-ceba_interactive_exercises_meeting_prep.md (cwd=C:\Users\tukum\Downloads\remote\ceba, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b31a-7791-8af0-62e3e62e258e.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b31a-7791-8af0-62e3e62e258e, no follow-up correction; user ended with /exit so no explicit acceptance)

### keywords

- CEBA interactive exercises, Anh brainstorm, HTML report, fun simple content-fit, DPPA calc, PV BESS sizing, 21 Jul alignment recap, agenda spreadsheet probe-slice

## User preferences

- "unslop, update and retract into a 2 page doc" -> plain decision-ready language, current status, and strict length control; "ind stay dropped, northern keep, move to hp" is binding project scope [Task 2]
- when the deck ran over brief (16 versus 8-12 slides), the user chose: "Keep 16, mark FLEX" -> keep all slides and mark 3-4 skippable live rather than cutting content [Task 3]
- when asked revision scope, the user chose: "English PPTX only" -> revise the build script to v2.2 English only and defer HTML/VI/ZH to avoid double translation [Task 3]
- when reviewer wording conflicts with an agent style rule, client wording wins verbatim -> adopt Lauren titles exactly and drop the no-you-in-title assertion (kept no-leading-So/And) [Task 3]
- when the user said: "implement full plan then git commit push" -> implement all phases, commit and push without further prompts, keeping unrelated files out of the commit [Task 3]
- when prepping for an internal meeting, the user said: "prep for that meeting on my behalf using all available context with my intention for these sessions to be fun, simple but perfectly suited for delivering the content needed, synthesized prep into html report" -> default to exhaustive context synthesis, filter proposals through fun plus simple plus content-fit, and deliver as an HTML report [Task 4]

## Reusable knowledge

- Reuse `Downloads/.fmt/build_sow.py` house style; explicit `C:\Program Files\LibreOffice\program\soffice.exe` plus `pdfinfo` verified exactly two pages. [Task 2]
- Withheld from the external SOW: fees/rates, cost-split, staff names/workloads, retainer scope-limitation clause, Open Items (location, Indonesia, Output 2, KBC/SHP scenario, JD re-issue), ViDA pilot size/Senergy JV/KBC link, CPI/CFM fund-manager note, workbook defects, dated CPI Lab milestones. Updated to base year 2025, ex-Hai Phong data in / ex-Hai Duong due Oct, draft baseline under review to DAE Dec 2026, east/west advisory, ViDA pilot designed plus in CPI Lab, Gap Stage 1 ranking/financing options framed around clean heat/EE. Page-count check pattern is soffice --headless --convert-to pdf plus pdfinfo Pages plus pdftoppm render; hp/ is gitignored so drafts and build scripts are safe there. [Task 2]
- EE deck house style from the Oct Day1 combined deck: short Title Case noun phrases 2-7 words, often Label: Subject, never leading So/And; sessions open with a Session X.Y divider plus About the Speaker and close with Q and A plus Key Takeaways. Local source is ceba/render/build_ee_pptx.py with prototype ceba/render/ee-deck-prototype.html and the active plan in ceba/activeContext.md; Drive v2.1 fileId 1ucPNSV2bvzcLrmPSc9FXQ-Q9crLyPpdm in folder 1eTbuY58vnzTAN74-7_KVr-yxHykCs8wm is invisible to gws drive (403/404) and to personal-Gmail Chrome, so rely on Gmail comment emails plus Drive read_file_content text. [Task 3]
- EE v2.2 TDD pattern that worked: ceba/render/test_ee_deck.py with 7 tests written red (7 failed) then green after edits, covering titles, Lauren S2 wording, Cong handoff, resources split, Applies-to lines, notes plus FLEX, and no em-dashes; build defaults to v2.2 only (16 slides, near 6.2MB) with --full keeping stepped plus VI/ZH (stale); QA is LibreOffice soffice --headless --convert-to pdf plus PyMuPDF overlap/overflow check (qa.py) plus contact-sheet review, with header() TEXT_TO_FIT_SHAPE needed for long titles (autofit enabled for all languages, not LANG-gated). [Task 3]
- Drive silent-edit detection: no new comment notifications arrived, but Drive v2.1 modifiedTime 2026-09-11T20:56Z (15min after Lauren email, size changed) showed she retyped S2-S10 titles with no email -> always check modifiedTime/size, not comment emails; adopted titles kept verbatim (Efficiency Reduces the Energy You Have to Buy; Successful Efficiency Examples in Vietnam; The Case for Efficiency: Two Part Electricity Tariff; Understanding the Flow of Electricity At Your Facility; Compressed Air is A Major Cost Driver; Excess Heat is a Value You Have Already Paid For; Understanding the Business Case: Waste Heat Recovery; Precision Requires Power; Refrigeration and Cooling are Key Cost Drivers). [Task 3]
- Meeting-prep context that held: Oct 2026 Hanoi workshop is 15-16 Oct 2026 at Grand Mercure Hanoi with the internal brainstorm on 17 Sep 2026 14:00-15:00 ICT hosted by Hong Anh Le; for Oct 2026 agenda work the 21 Jul alignment call recap is authoritative, not ops/internal-alignment-memo_Oct2026.md which was never circulated; governing CEBA asks were the interactive design plan before the next weekly call and draft slides due Sep 29, with a lighter less-demanding end-of-day exercise promised against afternoon fatigue. Report calls pushed were 45-min Size the Factory (not near 1hr Excel), moving the Day2 calc after strike-vs-spot teaching with the 11:00-12:00 overlap fixed, cutting end-Day2 105 to 70 min, and flagging the DPPA worksheet answer key as backwards (buyer pays generator when spot below strike, net 1850 VND/kWh). [Task 4]
- Large Drive sheets/decks exceed token limits on direct read -> probe-then-slice with jq/python into a local scratchpad file (scratchpad/agenda.txt pattern) from the start, with PYTHONIOENCODING=utf-8 set explicitly on Windows. [Task 4]

## Failures and how to do differently

- Do not disclose unsettled fees, staffing commentary, or unresolved counterparties in external SOW drafts. Set `PYTHONIOENCODING=utf-8` for Unicode and avoid `sed` path rewrites on Windows. [Task 2]
- Direct Drive edits (<FINANCE_CONTACT> S14 titles, Lauren S2 lines) are not in the local build script, so a rebuild overwrites them -> Phase 0 must port Drive text back into the script first and add speaker-notes support (the script wrote no notes); v2.2 at 6MB cannot upload via the Drive connector or gws, so leave upload to the user. [Task 3]
- Test assertion edits can fail via backslash escaping through the tool -> use sed line-based edits for assertion strings. [Task 3]

# Task Group: unslop skill sync across five harnesses
scope: Update the unslop writing-review skill in every harness from one source of truth, keeping SKILL.md tight and moving the review workflow to a reference file.
applies_to: cwd=~/.agents/skills/unslop (source of truth); reuse_rule=procedure is general, but paths are machine-specific; opencode loads skills at start so it needs a restart

## Task 1: Sync unslop tells 32-35 plus house-voice across claude/hermes/omp/opencode/codex, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-oWdp-ceba_ee_v2_2_revision_and_unslop_sync.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b309-7450-af5f-330dfd204b57.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b309-7450-af5f-330dfd204b57, copies verified by diff; opencode/codex harnesses untested without a session)

### keywords

- unslop, SKILL.md, review-feedback.md, tells 32-35, house-voice, hermes skills, opencode debug skill, omp discovery, codex prompts unslop.md, AGENTS.md pointer

## User preferences

- when asked skill scope, the user chose: "SKILL.md + reference file" -> keep SKILL.md a tight tells checklist, add tells 32-35 plus house-voice, and put the 12-step review workflow in references/review-feedback.md [Task 1]
- when asked sync method, the user chose: "Copy once, no script" -> write the files into each location now and accept future drift [Task 1]
- when asked codex wiring, the user chose: "Slash command + AGENTS.md pointer" -> generate ~/.codex/prompts/unslop.md for /unslop plus an always-apply rule in AGENTS.md [Task 1]
- when asked hermes registry copy, the user chose: "Edit in place" -> edit ~/AppData/Local/hermes/skills/unslop/ despite its url source, tracking as user-modified is OK [Task 1]

## Reusable knowledge

- Source of truth is ~/.agents/skills/unslop/ (SKILL.md plus references/review-feedback.md); identical copies go to ~/.claude/skills/unslop/, ~/AppData/Local/hermes/skills/unslop/, ~/.config/opencode/skills/unslop/; omp needs no copy (discovers .agents/.claude/.omp/.opencode skills); codex gets a generated prompt via codex_unslop.py plus a pointer in ~/.codex/AGENTS.md. New tells 32-35 are conversational titles, slogans, telegraphic fragments, and irreconcilable figures. [Task 1]
- Verification: diff -rq copies versus source; opencode debug skill shows the unslop entry with the new section (needs full JSON capture and a restart since opencode loads at start); hermes skills list still enabled; omp/codex stay untested without a model session and must be disclosed as such. [Task 1]

## Failures and how to do differently

- Skill listings can be incomplete: when the user names a skill, call it and never declare it missing from a listing (unslop was present but the listing missed it). [Task 1]
- Bash heredoc quoting breaks on review-feedback content (unexpected EOF) -> use the Write tool for patch scripts and the reference file, then cp. [Task 1]
- hermes skills list and opencode debug skill calls time out -> run with timeout and read background output files. [Task 1]

# Task Group: GTB Drive implementation, BIDV crosswalk, and time-off operations
scope: Maintain GTB implementation structures and crosswalk methodology; sync bilingual BIDV NDA redlines with tracked changes; draft PCAF outreach emails as unsent drafts; perform live operations only after authentication and read-back verification.
applies_to: cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb and cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=Drive/TSheets state is live and time-specific

## Task 1: GTB 2026 Drive organization and tracker, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-40-puuT-gtb_2026_implementation_folder_setup.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-40-01a0e1d3-a8d4-7a50-9e0a-bdb666871b6b.jsonl, updated_at=2026-09-27T07:45:40+00:00, thread_id=01a0e1d3-a8d4-7a50-9e0a-bdb666871b6b, tree and tracker read back)

### keywords

- Implementation GTB 2026, Outputs 1.1-4.4, shortcuts, Skip uploads, activeContext.md

## Task 2: BIDV Open CEDA/PCAF crosswalk v0.9, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-yvXV-bidv_fe_code_crosswalk_v01_v09.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a557-7812-b570-eea8f0ee8dff.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a557-7812-b570-eea8f0ee8dff, 51 tests pass)

### keywords

- BIDV_OpenCEDA_crosswalk_v0.9.xlsx, 587 codes, Open CEDA 2025, PCAF, desc_audit_10.csv, 51 tests

## Task 3: TSheets leave/Vietnam holiday corrections, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-39-7yxP-tsheets_leave_holiday_correction_sep_2026.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-39-01a0e1d3-a532-7b41-9546-6558fdc28d81.jsonl, updated_at=2026-09-27T07:45:39+00:00, thread_id=01a0e1d3-a532-7b41-9546-6558fdc28d81, live corrections require review)

### keywords

- TSheets, time off, Vietnam holidays, leave corrections, QuickBooks Time

## Task 4: BIDV English NDA Drive upload and review-email draft, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-dgeo-bidv_english_nda_drive_upload_draft_email.md (cwd=C:\Users\tukum\Downloads\pacta-trisk, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b5cc-73f3-b024-acc665792984.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b5cc-73f3-b024-acc665792984, Gmail MCP cannot download attachments so gws is required; draft staged not sent)

### keywords

- BIDV, NDA, gws CLI, Gmail attachments, Google Drive upload, GTB 2026-2027, Lauren McGinley, <FINANCE_CONTACT>

## Task 5: Sync Vietnamese BIDV NDA to revised English NDA with tracked changes, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-aZzT-bidv_nda_vietnamese_tracked_redline.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b288-7433-ab14-de01770e4ac5.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b288-7433-ab14-de01770e4ac5, reject-all equals BIDV original in both rounds; BIDV-facing copies saved; nothing sent)

### keywords

- BIDV NDA, VIE-ENG redline, tracked changes, Tung Ho, Lauren McGinley, Zone.Identifier, Word COM, OOXML, lxml, pandoc, MST 0317819013, +(84) 0917778477

## Task 6: Draft PCAF intro emails to Techcombank and EuroCham SFSC, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-6JwV-pcaf_intro_drafts_techcombank_eurocham_sfsc.md (cwd=C:\Users\tukum\Downloads\pacta-trisk\gtb, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b2e2-7942-88fe-e0a6d7e064cd.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b2e2-7942-88fe-e0a6d7e064cd, two unsent Gmail drafts; Vietcombank and VietinBank intros uncovered)

### keywords

- PCAF, Tiange Wei, Techcombank, EuroCham SFSC, Giandomenico Zappia, Huongctl4, Gmail drafts, introduction email, Hanoi Sep30-Oct2

## User preferences

- for existing Drive files, user chose “Shortcuts”; for laptop-only files, “Skip uploads” -> preserve originals and do not upload local files unless explicitly requested [Task 1]
- BIDV “only do the code matching and return to them” -> crosswalk-only boundary; do not request loan/emissions databases. “less words more visual” -> concise HTML visual artifacts with detail in workbook/methodology [Task 2]
- when sharing BIDV legal docs, the user said there is usually not much room for review with a bank like BIDV as their template is standard and rock solid -> future drafts sharing BIDV templates should include that framing and recommend only pushing back on real blockers [Task 4]
- when updating bilingual legal docs, the user said: "make sure that the vietnamese version is updated accordingly in tracked change" -> keep originals untouched, do all edits with Track Changes on, and preserve reject-all == original [Task 5]
- when asked to send or act externally, the user said: "strip and do not send anything on my behalf, i'll do it myself" -> prepare local or BIDV-facing files only with internal threads stripped, and let the user send [Task 5]
- when choosing intro recipients and style, the user selected Giando plus Anh Trinh for EuroCham, Huong plus Thanh plus Ngoc for Techcombank, and direct joint intro with Tiange copied -> for this PCAF case default to direct joint English intros copying the wider known teams rather than ask-first pre-checks [Task 6]

## Reusable knowledge

- GTB tree follows signed outputs 1.1–4.4; output 2.2/4.3 lacked matching prior deliverables. Fix Windows encoding with `PYTHONIOENCODING=utf-8` and invoke native `gws.exe`; verify final tree and tracker. [Task 1]
- v0.9: 587 codes, 339 H/232 M/16 L, 51 tests, and 224 audited full-description rows. Keep match confidence distinct from PCAF DQ; fossil power is H because CEDA description covers fossil generation, renewables M. [Task 2]
- Gmail MCP search_threads/get_message can list attachment filename/ID but cannot download bytes; use gws gmail users messages get/attachments get for download, then gws drive files create --upload for Drive upload. [Task 4]
- BIDV GTB Drive folder 10eJhcsLiWg68v5lz2X5sJwjYewxomenG holds MoU v2 plus the Vietnamese NDA; the uploaded English NDA kept the BIDV original name/format as 1Ga6ldgrSFpTFxxYmO5KBIgoEnVjgcq5v. Source message 1a08ad610b9ff56e (2026-09-10, 8 pages, mutual NDA to 31 Dec 2027, 5yr tail); review draft r-8413759618406180036 to <EMAIL> and <EMAIL>, not sent. [Task 4]
- VIE NDA originals were duplicate old .doc files; convert via Word COM SaveAs2 to a clean .docx with 0 revisions before redlining, author insertions as Tung Ho, and validate with pandoc --track-changes reject/accept plus the docx validator. Use PowerShell Copy-Item -LiteralPath for diacritic filenames and set PYTHONIOENCODING=utf-8 for Vietnamese output; render PDFs with PyMuPDF fitz when pdftoppm is missing. [Task 5]
- Word COM hangs on Documents.Open when Mark-of-the-Web Zone.Identifier forces Protected View: Unblock-File, clear HKCU Word Resiliency plus .asd plus ~$ locks, and if opens still hang switch to direct OOXML edits with lxml plus python zipfile repack preserving entry order (shell zip is missing); in tracked docs search accepted text, not deleted runs, and always render the untouched file the same way as a layout control. [Task 5]
- PCAF contact map: Tiange (Thea) Wei <EMAIL> (APAC plus Greater China Lead, Hanoi Sep30 afternoon and Oct1-2, targeting Vietcombank, VietinBank, Techcombank plus associations and regulators; BIDV first VN bank to join); Techcombank Chu Thi Lan Huong <EMAIL> plus thanhnnh@ plus ngocld3@; EuroCham SFSC Giandomenico Zappia <EMAIL> plus coordinator Anh Trinh <EMAIL>. Two unsent drafts exist (Techcombank thread 1a0af694743257fb, EuroCham thread 1a0af6973c1f1cb7); flag unverified items (Giando title, Trang domain, TCB meeting agreement) before sending. [Task 6]
- Large Gmail threads exceed token limits (62k chars observed) -> probe structure with jq, then slice per-message text in python by splitting on reply markers. [Task 6]

## Failures and how to do differently

- Require full-description clauses and independent spot checks; snippet/keyword classification caused bad sector ratings. Assert changelog equals direct version diff; second coder/sign-off remains needed. [Task 2]
- Treat time-off/holiday corrections as partial until live-system read-back confirms affected entries; do not infer state from export alone. [Task 3]
- PowerShell gws --params with single-quoted JSON fails with Invalid --params JSON; use Bash with single-quoted JSON in this environment. [Task 4]
- Python printing Vietnamese filenames under cp1252 fails with UnicodeEncodeError; set PYTHONIOENCODING=utf-8, redirect to file, or write bytes locally before inspecting. [Task 4]
- ripgrep/Glob over Downloads timed out; list recent Downloads via Get-ChildItem sorted by LastWriteTime and walk Gmail payload.parts directly. [Task 4]
- A Cohort 6 Years 9-12 recovery-tail question (extend grid to Y13 vs truncate vs flag post-fund-life) was left unaddressed when the rollout moved on -> explicitly answer or queue such questions rather than silently dropping them. [Task 5]
- Gmail search can return service unavailable mid-run -> proceed from known contacts instead of retry-looping. [Task 6]

# Task Group: pacta-trisk architecture review and artifact-catalog planning
scope: Run autonomous codebase/architecture reviews with subagent walks, serve the HTML report locally for visual check, and turn strong candidates into phased plans without implementing.
applies_to: cwd=C:\Users\tukum\Downloads\pacta-trisk; reuse_rule=repo-family procedure (codebase-design and plan skills); verify R/ layout and Wave status before reuse

## Task 1: Autonomous architecture review to HTML, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-vT48-pacta_trisk_architecture_review_artifact_catalog.md (cwd=C:\Users\tukum\Downloads\pacta-trisk, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b7a1-7132-b8a0-12cfdd84ae94.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b7a1-7132-b8a0-12cfdd84ae94, main at bd09f48 Wave 5 landed; INVARIANTS PASS)

### keywords

- codebase review, architecture review, artifact catalog, engagement_plan.R, step_registry.R, verify_refactor.R, mermaid, INVARIANTS, Wave 5

## Task 2: Grill candidate A plus CONTEXT, ADR, and plan, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-43-vT48-pacta_trisk_architecture_review_artifact_catalog.md (cwd=C:\Users\tukum\Downloads\pacta-trisk, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-43-01a0e1d3-b7a1-7132-b8a0-12cfdd84ae94.jsonl, updated_at=2026-09-27T07:45:43+00:00, thread_id=01a0e1d3-b7a1-7132-b8a0-12cfdd84ae94, grill record plus CONTEXT.md plus ADR 0001 plus 5-phase plan; implemented nothing)

### keywords

- artifact-catalog-design-grill, CONTEXT.md, ADR 0001, 5-phase plan, 67 rows, sector_registry, snapshot contract

## User preferences

- when absent, the user said use judgement for any task requiring user input in the meantime -> proceed autonomously and record decisions for later review [Task 1]
- after interruption, the user said Proceed -> resume the same work (git log, registry reads) without re-asking [Task 1]
- the user said proceed with turning candidate A into a plan -> use the plan skill, inline the research, produce the phased plan, implement nothing, and leave go-ahead to the user [Task 2]

## Reusable knowledge

- Highest friction found: artifact-path knowledge has no owner with 16 files spelling the same CSV paths; Wave5 plan-file checkboxes read 0/97 while NEWS says landed, so trust NEWS.md. [Task 1]
- Catalog shape decided: key, engagement_path (cfg-derived), snapshot_path (relative), gated/disclaimer flags, row_count; PACTA 6 CSVs plus figures dir, TRISK 14+3 per sector, 4 analytics, manifests, 7 gated HTMLs; correct row count is 67 (13 engagement plus 54 sector), computed not hardcoded. [Task 2]
- Report serving: browsers cannot open file URLs, so serve Temp on 127.0.0.1 and navigate to http; verify mermaid rendered with 0 errors, then kill the server via netstat plus taskkill. [Task 1]

## Failures and how to do differently

- Bash heredoc for large HTML fails ENAMETOOLONG; use the Write tool for HTML reports. [Task 1]
- sector_prioritization plus analytics copy reads the previous-run Snapshot; the plan deliberately preserves ordering and records reordering as follow-up. [Task 2]

# Task Group: Google Workspace CLI authentication and Slides comment synthesis
scope: Verify gws OAuth/service access and retrieve complete Drive comments before producing a filtered Markdown review.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp and cwd=C:\Users\tukum\Downloads\ee-heat; reuse_rule=account and deck state are live; verify current auth/scopes and re-fetch comments on each run

## Task 1: Authenticate work gws account and assess Openwork OAuth client, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-50-39-mnj9-gws_work_oauth_openwork_drive_and_cli_desktop_visibility.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-50-40-01a0e1d8-3bf7-7000-8b8a-549b00515f4f.jsonl, updated_at=2026-09-27T08:33:14+00:00, thread_id=01a0e1d8-3bf7-7000-8b8a-549b00515f4f, Gmail and Drive live calls succeeded)

### keywords

- gws, gws-work, GOOGLE_WORKSPACE_CLI_CONFIG_DIR, OAuth, Openwork, my-workspace-cli-2026, gmail.modify, client_secret.json, localhost callback, Codex desktop threads

## Task 2: Retrieve energy-efficiency deck comments for Markdown synthesis, partial

### rollout_summary_files

- rollout_summaries/2026-09-27T08-26-47-qG1t-google_slides_energy_efficiency_comments_synthesis.md (cwd=C:\Users\tukum\Downloads\ee-heat, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T15-26-48-01a0e1f9-4f5f-7653-8468-158788033dd3.jsonl, updated_at=2026-09-27T08:43:52+00:00, thread_id=01a0e1f9-4f5f-7653-8468-158788033dd3, both comment pages retrieved; synthesis not delivered)

### keywords

- Google Slides, Drive comments, comments.list, nextPageToken, pageToken MTAw, fields inside --params, energy efficientcy section, Markdown, 156 comments

## User preferences

- when the user asked "gws should be signed in no?" and requested a link -> verify live auth rather than assuming config equals credentials, then provide the browser OAuth URL when consent is waiting [Task 1]
- when the user asked why "Openwork" was safe -> explain consent-screen branding, client provenance, and requested scopes before recommending consent [Task 1]
- when the user asked to "synthesize for me in markdown" for the "energy efficientcy section" -> return an organized, section-filtered Markdown synthesis rather than a raw export [Task 2]

## Reusable knowledge

- Set `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` to the intended config before every `gws` command, then verify with a live service call such as `gws gmail users getProfile --params '{"userId":"me"}'`. `gws auth status` alone is not enough. [Task 1]
- An OAuth label comes from the stored Google Cloud client/project branding, not from gws itself. Broad consent includes Gmail modify, Drive, Sheets, Calendar, Docs, Slides, and Tasks, so verify the client owner before accepting. [Task 1]
- This CLI expects `fields` inside JSON `--params`. Drive comments are paginated: follow every `nextPageToken`. The deck had 156 comments across 100-item and second-page requests. [Task 2]

## Failures and how to do differently

- PowerShell quoting can corrupt JSON; use single-quoted JSON with `--params`, or Python argument arrays when nesting becomes complex. Cast parsed date values to `[string]` before concatenating, and use `Join-Path $env:TEMP 'ee_comments.json'`. [Task 1][Task 2]
- Do not call comment analysis complete after retrieval. Map anchors/quoted content to slides, filter the requested section, and group the feedback by content, tone, evidence, structure, and visual design before delivering Markdown. [Task 2]
- Evidence shows selected local Codex CLI sessions appeared in the desktop thread list. It does not prove universal CLI/Desktop synchronization. [Task 1]

# Task Group: Gmail HoldForBatch and calendar-notice automation
scope: Maintain live Gmail batching with Apps Script as the sole label/release authority and fail-safe calendar-notice filtering.
applies_to: cwd=C:\Users\tukum\Downloads\remote\temp; reuse_rule=live account state; inspect current triggers/auth/scopes before any change

## Task 1: Simplify HoldForBatch with VIP removal plus calendar-notice clearing, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-41-ykLV-gmail_holdforbatch_vip_removal_calendar_clearing.md (cwd=C:\Users\tukum\Downloads\remote\temp, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-41-01a0e1d3-ae98-7bc1-abea-8552452f71bb.jsonl, updated_at=2026-09-27T07:45:41+00:00, thread_id=01a0e1d3-ae98-7bc1-abea-8552452f71bb, VIP allowlist deleted, 96 plus 25 invite-noise threads swept with undo records, calendar-notice job deployed and trigger-verified)

### keywords

- HoldForBatch, Batch Email Delivery, holdIncomingMail, deliverBatchedMail, archiveCalendarNotices, clasp, 10:30 ICT, VIP_SENDERS deleted, calendar prefixes, gmail.settings.basic, category:primary

## User preferences

- when the inbox looked messy, the user said they just want a simple process of emails being held in a label like holdforbatch -> simple hold-until-10:30 model held weekends/vacation; brainstorm first for unclear parts [Task 1]
- when asked about VIP exemption details, the user said everything can be batched with no VIP list -> delete the allowlist entirely and accept same-day deadline deferral to 10:30 [Task 1]
- when asked what to do with invites, the user chose archive-all-except-cancellations then in-script over Gmail filter -> prefers the version-controlled Apps Script solution needing no new OAuth scope [Task 1]

## Reusable knowledge

- Deploy `apps-script\hold-for-batch.gs` via `deploy.ps1 -Live`; confirm local/deployed `Code.js` equality. When schedules change, run `setupTriggers()` once and verify exactly `holdIncomingMail` every 5 minutes plus `deliverBatchedMail` daily around 10:30. [Task 1]
- Gmail `IMPORTANT` and `INBOX` are independent. Hermes jobs must not strip `HoldForBatch`; use `hermes cron edit`, not direct jobs JSON edits. [Task 1]
- `archiveCalendarNotices()` uses exact anchored Calendar-generated subject prefixes; it deliberately leaves `Canceled:` notices and human threads with `.ics` attachments visible. [Task 1]
- Final hold query: `in:inbox is:unread -is:starred -is:muted -from:me -filename:invite.ics -label:HoldForBatch -label:BatchReleased newer_than:3d`; the VIP substring had matched the user own address and permanently exempted replied threads, so deleting the list removed 3 rounds of compensating bugs. Query `category:primary` explicitly because bare `in:inbox` spans tabs; `resultCountEstimate` always reads near 201 so verify by paging/probes. [Task 1]
- Gmail filters evaluate per-message while search is per-thread, so a reply exclusion is safe in filters but not verifiable via search. `gws filters.list` works but `filters.create` needs `gmail.settings.basic` the token lacked; the script needs no `setupTriggers()` rerun when riding the existing trigger, and secondary jobs go in try/catch so they never block intake. [Task 1]

## Failures and how to do differently

- Never use `filename:invite.ics`/loose keywords as a calendar filter: Gmail tokenization and threads overmatch human client correspondence. `gws` can list filters but lacked `gmail.settings.basic` for creation; use Apps Script and fail-safe message-by-message prefix checks. [Task 1]
- Browser Apps Script edits may be classifier-blocked. Deploy version-controlled local source with `clasp`; do not rerun trigger setup for code-only changes on existing schedules. [Task 1]

# Task Group: Postpartum daily-log clinical-insights artifact
scope: Create an informational, clinician-review-oriented artifact from postpartum logs without diagnosis or unsupported analytics claims.
applies_to: cwd=C:\Users\tukum\Downloads\baby-context; reuse_rule=sensitive and time-specific; never treat this as medical advice or a clinical diagnosis

## Task 1: Assess postpartum log against consensus, qualitative insights artifact success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-38-5MC0-linh_postpartum_insights_html_artifact.md (cwd=C:\Users\tukum\Downloads\baby-context, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-38-01a0e1d3-a26f-7e70-82f1-27d82c1e7bec.jsonl, updated_at=2026-09-27T07:45:38+00:00, thread_id=01a0e1d3-a26f-7e70-82f1-27d82c1e7bec, qualitative insights artifact; clinical validation absent)

### keywords

- postpartum, linh_clinical_handoff.md, EPDS, GAD-7, bleeding, transvaginal ultrasound, clinical insights, generate-report.py, linh_daily_log_raw.json, 2026-09-25-linh-postpartum-insights.html, ACOG NICE

## User preferences

- when asking for a clinical read, the user said assess the daily log analytics and provide qualitative insights for my wife against medical consensus for postpartum issues in html artifact -> prefers qualitative interpretation mapped to medical consensus (ACOG/NICE/FIGO/ATA) in a shareable HTML artifact, not just a quantitative dashboard [Task 1]

## Reusable knowledge

- Reconcile report analytics to raw log rows before clinical claims: prior logic said GAD-7 absent despite raw data. EPDS interpretation may not use standard cutoffs if an observer completed it. [Task 1]
- Flag bleeding, thermal symptoms, pain, iron-related hard stool, and herbal/TCM use for clinician review, not diagnosis. Private artifact sharing must be enabled via Share menu for family/clinicians. [Task 1]
- Source pipeline: reports/2026-09-25-linh-daily-log-analytics.html (Sep 8-24, 17/17 nights) generated by services/linh-form/generate-report.py from reports/data/linh_daily_log_raw.json (fetched by fetch-sheet.py); clinical context in mom/linh_clinical_handoff.md plus mom/linh_clinical_tracking_v1.0.json; new qualitative artifact is reports/2026-09-25-linh-postpartum-insights.html. The generate-report.py GAD-7 detection bug was left unfixed; raw JSON holds GAD-7 answers for both weeks. Set PYTHONIOENCODING=utf8 before HTML text extraction to avoid cp1252 errors. [Task 1]

## Failures and how to do differently

- Do not repeat unsupported claim that GAD-7 changed 6→17: only one raw block was evidenced. No user/clinical validation occurred, so describe artifact as an informational aid only. [Task 1]

# Task Group: Toggl postpartum health timeline mining and artifact
scope: Mine the local Toggl SQLite log for wife postpartum health signals since a stated date and publish a private HTML timeline artifact with source rows plus doctor questions.
applies_to: cwd=C:\Users\tukum\Downloads\toggl-api; reuse_rule=sensitive and time-specific; keep artifacts private and frame clinical notes as questions, never diagnoses

## Task 1: Mine Toggl log for wife health periods since May 2026, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-0ztN-toggl_wife_health_timeline_artifact.md (cwd=C:\Users\tukum\Downloads\toggl-api, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b2c2-7520-9aeb-37c0b81519d3.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b2c2-7520-9aeb-37c0b81519d3, 2095 entries mined; periods A-E identified)

### keywords

- toggl, time_entries, toggl.db, postpartum, hot-cold sweat, fever, PPD, hits.txt, postpartum-health-log.html

## Task 2: Synthesize HTML timeline artifact and publish private, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-42-0ztN-toggl_wife_health_timeline_artifact.md (cwd=C:\Users\tukum\Downloads\toggl-api, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-42-01a0e1d3-b2c2-7520-9aeb-37c0b81519d3.jsonl, updated_at=2026-09-27T07:45:42+00:00, thread_id=01a0e1d3-b2c2-7520-9aeb-37c0b81519d3, 66 embedded rows; private artifact; share-via-menu instruction given)

### keywords

- artifact-design, postpartum-health-log.html, timeline, filterable table, thyroid TSH/FT4, grep count, jitter fix

## User preferences

- when asking for a health timeline, the user said: "Check my toggl log to pinpoint periods since May 2026 when instances of hot cold sweat or general health issue with my wife start then synthesize in html artifacr" -> default to exhaustive log search since the stated date plus a shareable HTML artifact timeline, not just a chat list [Task 1]
- when publishing health timelines, keep the artifact private, tell the user to use the Share menu before showing a doctor, and exclude in-laws visits plus own sleep and mood unless requested [Task 2]

## Reusable knowledge

- Toggl store is SQLite at `data/toggl.db`, table `time_entries` with columns description, start, stop, duration_hours, project_name, tags; May1-Sep12 2026 held 2095 entries. [Task 1]
- Two-pass regex is needed: first wife-name keywords plus symptom and care terms, then physical terms (temp, hot, cold, fan, aircon, flash, med, FV, period, thyroid, hormon, PPD, HB, CIH, obgyn) to catch entries without wife keywords. Found periods: A 13-20 May low-temp/fever plus engorgement and stop-breastfeeding; B 26 Jul incapacitating hot-cold flashes plus 29 Jul med check plus 30 Jul FV treatment plus 2 Aug night sweat; C 28 May first PPD signs to 18 Aug formal diagnosis; D 24 Aug-12 Sep temp complaints plus san hau phong wind diagnosis; E 11 Sep abnormal period CIH check. Night pattern is durable: fever, sweats, and hot-waking happen overnight even when logged later. [Task 1]
- Build the timeline with the artifact-design skill as a clickable timeline plus filterable source table plus doctor questions (thyroid TSH/FT4 framed as question, not diagnosis); verify embedded row counts with grep before writing copy (66, not 74). [Task 2]

## Failures and how to do differently

- A broad first regex dumped 37KB into context -> redirect full chronological hits to a scratchpad file and read it paged instead of printing to stdout; on session-limit resume, read the scratchpad directly instead of re-querying. [Task 1]
- Preview or render-check visual artifacts before publishing when possible; the first publish went out unpreviewed. [Task 2]

# Task Group: Sponsor training costs and official airline research
scope: Research official direct-flight options and assemble sponsor-facing training-cost workbooks/email drafts.
applies_to: cwd=C:\Users\tukum\Downloads\city-ghg; reuse_rule=prices, schedules, and project placement are time-specific; official fare evidence is required

## Task 1: SFO-HAN airline-direct airfare quoting plus SHP contract research plus training-cost workbook, success

### rollout_summary_files

- rollout_summaries/2026-09-27T07-45-40-coYW-sfo_han_business_airfare_training_cost_shp_contract.md (cwd=C:\Users\tukum\Downloads\city-ghg, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\27\rollout-2026-09-27T14-45-40-01a0e1d3-ab2f-7e23-8fd4-d3a8a94726c2.jsonl, updated_at=2026-09-27T07:45:40+00:00, thread_id=01a0e1d3-ab2f-7e23-8fd4-d3a8a94726c2, 9 tasks: LAX/SFO quotes, multi-city, airline-direct repricing, SHP contract, workbook, ranked PDF v5 final order United over STARLUX over China over PAL over ANA over EVA)

### keywords

- SFO-HAN business class, airline-direct, Josh Margolis, united.com, evaair, china-airlines des-portal, STARLUX, Philippine Airlines, Gmail drafts google.com/url redirect, gws raw-MIME upload, SHP Contract 01/HDTV-SHP-2025, training-cost workbook, Josh_SFO-HAN_airfare_ranked_2026-09-21.pdf

## User preferences

- when the user said "Josh will buy from official airlines" -> quote airline-direct fares only and label agency/Google-Flights prices as non-equivalent; treat official fare results as unverified until a screenshot contains the actual result [Task 1]
- when drafting, the user said "in my own style" and "I will send myself" -> create drafts only, never send, and match short Tung Ho style ("Warm regards, Tung") [Task 1]
- when links wrapped, the user asked to "Fix the links" -> deliver direct links, not Redirect Notice pages; the Gmail MCP tool rewrites every href into google.com/url redirects, so fix via gws CLI raw-MIME upload with --upload-content-type message/rfc822 [Task 1]
- when the workbook was in Downloads/scratchpad, the user asked to move it to the project folder and gitignore if uncommittable -> deliverables live in the project folder (training-costs/), never exiled to Downloads/temp [Task 1]
- when revising per Lauren, remove Summary open-items and state Global Advisory selects options, connects to venue, pays venue/airlines/hotel directly -> keep the workbook neutral (Mid not Recommended) with actions in the transmittal email not the sheets [Task 1]

## Reusable knowledge

- 21 Sep 2026 airline-direct reference prices for SFO-HAN business class, 1 adult, Nov 1-6: PAL $4,562.53 (only under $6k), EVA agency $6,108, China Airlines $6,673, ANA $6,679, STARLUX from $6,972, EVA-direct $7,783, Cathay $7,218, United $9,240/$9,914. Josh own itinerary was $7,769.03 and he prefers United without stopovers. [Task 1]
- Signed SHP Contract 01/HDTV-SHP-2025: VND 3,832,000,000 ex-VAT (near USD 145,616 at 0.000038 USD/VND) / VND 4,138,560,000 incl 8% VAT; 40% advance VND 1,655,424,000 invoiced Sep 14. June 2026 $29k/$32k increase ask declined, re-signed at same value; final 13-Aug-2026 agreement limits Allotrope Activity 3 to insights and coordination support with 2 reports, no training-cost exclusion or KBC-pay clause. [Task 1]
- Workbook is training-costs/HaiPhong_ETS_Training_Cost_Estimate_2026-09-23.xlsx (Summary/Assumptions/Venue Options/Flight Options); totals Low $10,791 / Mid $12,926 / High $14,946 after hotel 4->3 nights fix; formulas LibreOffice-recalculated with zero errors; print landscape A4 fit-to-1-wide. Shortcut CLI review catches tie-out/formatting issues. Repo rule: training-costs/ plus flight-prices/ gitignored with CLAUDE.md prohibition comment. [Task 1]
- gws 0.22.5 adds --upload-content-type and +reply --attach --draft; upgrading 0.7.0->0.22.5 deleted undecryptable credentials.enc requiring gws auth login -s gmail. mcp update_draft can knock a draft out of thread; prefer create_draft with replyToMessageId. 176KB bodies exceed the Windows 32K command-line limit so use file upload, not --json inline. [Task 1]

## Failures and how to do differently

- Airline results can be CAPTCHA/tool constrained (EVA session timeout, China Airlines Akamai block, digital.evaair.com permission denied until allowed). Preserve the partial outcome and ask for human completion rather than guessing a price. [Task 1]
- xlsx skill recalc.py fails on Windows (AF_UNIX); use LibreOffice soffice.exe headless convert to recalc then openpyxl data_only check. Header "#" breaks openpyxl; use "No."/"Ref". [Task 1]
- Saved draft links must be verified character-for-character against tested searches via programmatic decode-compare; a typed multi-city link carried an extra leg caught only by decode-compare. [Task 1]

# Task Group: Official EVA Air multi-city fare lookup
scope: Fill the official EVA multi-city booking form and obtain price evidence; human CAPTCHA is an explicit handoff boundary.
applies_to: cwd=C:\Users\tukum\Documents\Codex\2026-09-17\check-the-price-on-official-website; reuse_rule=run-specific route/page state; use the official domain and require a fare-result screenshot

## Task 1: Fill EVA multi-city itinerary, partial

### rollout_summary_files

- rollout_summaries/2026-09-17T10-11-33-CyEX-eva_air_multicity_fare_check_captcha_blocker.md (cwd=C:\Users\tukum\Documents\Codex\2026-09-17\check-the-price-on-official-website, rollout_path=C:\Users\tukum\.codex\sessions\2026\09\17\rollout-2026-09-17T17-11-33-01a0aed9-a015-7ca2-ba89-40d4e0415923.jsonl, updated_at=2026-09-17T10:32:00+00:00, thread_id=01a0aed9-a015-7ca2-ba89-40d4e0415923, form filled; CAPTCHA blocked prices)

### keywords

- EVA Air, booking-multi.aspx, browser-control, captcha, #content_txt_From1, #btn_ok, BR17, BR385, BR386

## User preferences

- “official website” and requested screenshots -> use EVA’s official domain and preserve fare-result screenshot evidence, not third-party prices [Task 1]

## Reusable knowledge

- Direct Playwright navigation returned HTTP 403; attach to the user’s visible Chrome through Browser Control. The segment selectors are `#content_txt_From1`/`To1`/`Cal1` through segment 3; cabin is `#content_ddl_cabinclass`, submit `#btn_ok`. [Task 1]

## Failures and how to do differently

- CAPTCHA requires user entry and click of “Search and Book”; never visually guess it. No results/price were obtained. Pass Browser Control numeric parameters as integers, not floats. [Task 1]
