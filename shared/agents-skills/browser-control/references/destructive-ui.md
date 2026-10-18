# Destructive UI Recipe

For destructive UI work, such as deleting drafts when no CLI/API command exists,
use a two-phase read-confirm-verify flow. Do not confirm destructive actions in
the same script that first discovers candidates unless the user already approved
the exact stable identifiers/text.

Phase 1 inspects candidates and returns exact row text/IDs for user approval:

```js
await page.goto("https://example.com/items", { waitUntil: "domcontentloaded" })
await page.waitForTimeout(3000)

const rows = await page.locator("[role=row], tr").evaluateAll((nodes) => {
  return nodes.map((node, index) => ({
    index,
    text: (node.textContent || "").replace(/\s+/g, " ").trim(),
  })).filter((row) => row.text.includes("Draft"))
})

return { url: page.url(), title: await page.title(), rows }
```

Phase 2 acts only on approved rows. Scope clicks from stable row text or IDs, read
the confirmation dialog, and throw unless the dialog matches the approved action:

```js
const approvedTexts = ["Draft invoice A $10.00", "Draft invoice B $20.00"]

for (const approvedText of approvedTexts) {
  const row = page.locator("[role=row], tr").filter({ hasText: approvedText })
  if (await row.count() !== 1) {
    throw new Error(`Expected exactly one row for ${approvedText}`)
  }
  await row.locator("input[type=checkbox], [role=checkbox]").first().click()
}

const selected = await page.locator("input[type=checkbox]").evaluateAll((nodes) => {
  return nodes.map((node, index) => ({ index, checked: node instanceof HTMLInputElement && node.checked }))
    .filter((item) => item.checked)
})
if (selected.length !== approvedTexts.length) {
  throw new Error(`Expected ${approvedTexts.length} selected rows, got ${selected.length}`)
}

await page.getByRole("button", { name: /delete/i }).click()

const dialogText = await page.locator("[role=dialog], [aria-modal=true]").innerText()
if (!dialogText.includes(String(approvedTexts.length)) || !dialogText.match(/delete/i)) {
  throw new Error(`Unexpected confirmation dialog: ${dialogText}`)
}

await page.getByRole("button", { name: /delete|confirm/i }).last().click()
await page.waitForTimeout(1000)

return { approvedTexts, selected, dialogText, url: page.url() }
```

After confirming in the UI, verify independently with a fresh read path, such as
the app's list page, a CLI/API command, or a second `browser-control execute` that
reloads the page and checks the target rows are gone.

Never globally auto-accept native browser dialogs. If a native alert/confirm/prompt
is expected, use `page.waitForEvent("dialog")`, assert `dialog.type()` and exact
`dialog.message()`, then accept only that dialog.
