// The Herdr TUI's chrome, drawn in the app. One mod, one part per block:
//   props.part "spaces" | "agents" | "tabs", or props.pane for a pane's label.
// Click selects; right-click opens Herdr's own menu.

import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { spaces, agents, panes, props, run, openOverlay, setAgentOrder, shared, setShared, theme, window, layout } from "herdr";

const SIZE = 14;
const LINE = 20;
const GLYPH = { working: "●", blocked: "◉", done: "●", idle: "✓" };
const RANK = { blocked: 4, done: 3, working: 2, idle: 1 };

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

const width = () => find(layout(), "sidebar")?.size?.px ?? 230;
const narrow = () => width() < 120;

function toggleSidebar() {
  if (!narrow()) setShared("tui.sidebar", width());
  run("layout.resize", { id: "sidebar", px: narrow() ? (shared("tui.sidebar") ?? 230) : 44 });
}

function dot(t, status) {
  return div().flex_none().w(10).text_color(status ? t[status] : t.dim).child(GLYPH[status] ?? "·");
}

function menu(tab, target) {
  openOverlay({ mod: "menu", kind: "popup", width: 200, props: { tab, target } });
}

// A clickable word, as the TUI draws its buttons.
function word(t, id, label, action) {
  return div().id(id).flex_none().px(4).hover((s) => s.bg(t.hover))
    .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
    .on_click(action).child(label);
}

function header(t, title, right) {
  return h_flex().flex_none().h(LINE).mb(8).px(8).justify_between().items_center()
    .child(div().font_bold().child(title))
    .when(Boolean(right), (el) => el.child(right));
}

export default class Tui extends View {
  spacesPart(t) {
    const slim = narrow();
    const rows = spaces().map((s) => v_flex()
      .id(`space-${s.id}`)
      .flex_none()
      .px(8)
      .py(1)
      .when(s.active, (el) => el.bg(t.selected))
      .when(!s.active, (el) => el.hover((h) => h.bg(t.hover)))
      .on_click(() => run("space.select", { id: s.id }))
      .on_mouse_down("right", () => menu("space", { id: s.id }))
      .child(h_flex().h(LINE).gap(8).items_center()
        .child(dot(t, s.status))
        .when(!slim, (el) => el.child(div().flex_1().min_w(0).truncate()
          .when(s.active, (n) => n.font_bold().text_color(t.ansi15))
          .child(s.name))))
      .when(!slim && Boolean(s.branch), (el) => el.child(
        div().h(LINE).pl(18).truncate().text_color(s.active ? t.foreground : t.dim).child(s.branch ?? ""))));
    return v_flex().size_full().min_h(0).pt(6)
      .when(!slim, (el) => el.child(header(t, "spaces")))
      .child(v_flex().id("spaces-list").flex_1().min_h(0).overflow_y_scrollbar().children(rows))
      .child(h_flex().flex_none().h(LINE + 4).px(slim ? 0 : 4).justify_between().items_center()
        .child(word(t, "space-new", slim ? "+" : "new", () => run("space.new")))
        .when(!slim, (el) => el.child(word(t, "app-menu", "menu", () => run("app.palette")))));
  }

  agentsPart(t) {
    const slim = narrow();
    const priority = shared("tui.agents.sort") === "priority";
    const list = [...agents()];
    if (priority) list.sort((a, b) => (RANK[b.status] ?? 0) - (RANK[a.status] ?? 0) || b.seq - a.seq);
    setAgentOrder(list.map((a) => a.address));
    const rows = list.map((a) => v_flex()
      .id(`agent-${a.address}`)
      .flex_none()
      .px(8)
      .py(1)
      .mb(4)
      .when(a.focused, (el) => el.bg(t.selected))
      .when(!a.focused, (el) => el.hover((h) => h.bg(t.hover)))
      .on_click(() => run("agent.focus", { terminal: a.address }))
      .on_mouse_down("right", () => menu("pane", { pane: a.pane, terminal: a.address }))
      .child(h_flex().h(LINE).gap(8).items_center()
        .child(dot(t, a.status))
        .when(!slim, (el) => el.child(div().flex_1().min_w(0).truncate()
          .child(a.tab_name === String(a.tab_index) ? a.space_name : `${a.space_name} · ${a.tab_name}`))))
      .when(!slim, (el) => el.child(h_flex().h(LINE).pl(18).gap(0).items_center()
        .child(div().flex_none().text_color(t[a.status]).child(a.status))
        .child(div().flex_1().min_w(0).truncate().text_color(a.focused ? t.foreground : t.dim)
          .child(` · ${a.pane_name ?? a.program?.name ?? a.app ?? "agent"}`)))));
    return v_flex().size_full().min_h(0).pt(6)
      .when(!slim, (el) => el.child(header(t, "agents",
        word(t, "agents-sort", priority ? "priority" : "grouped",
          () => setShared("tui.agents.sort", priority ? "grouped" : "priority")))))
      .child(v_flex().id("agents-list").flex_1().min_h(0).overflow_y_scrollbar().children(rows))
      .child(h_flex().flex_none().h(LINE + 4).px(4).justify_end().items_center()
        .child(word(t, "sidebar-toggle", slim ? "»" : "«", toggleSidebar)));
  }

  tabsPart(t) {
    const space = spaces().find((s) => s.active);
    const tabs = (space?.tabs ?? []).map((c) => h_flex()
      .id(`tab-${c.id}`)
      .flex_none()
      .h(LINE)
      .min_w(58)
      .px(14)
      .justify_center()
      .items_center()
      .when(c.active, (el) => el.bg(t.accent).text_color(t.accent_foreground).font_bold())
      .when(!c.active, (el) => el.text_color(t.dim).hover((h) => h.bg(t.hover)))
      .on_mouse_down("left", (e, cx) => {
        cx.stop_propagation();
        if (e.click_count === 2) run("tab.rename", { id: c.id });
      })
      .on_click(() => run("tab.select", { id: c.id }))
      .on_mouse_down("middle", () => run("tab.close", { id: c.id }))
      .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); menu("tab", { id: c.id, space: space.id }); })
      .child(div().max_w(220).truncate().child(c.zoomed ? `${c.name} Z` : c.name)));
    const w = window();
    return h_flex().size_full().min_w(0).px(4).gap(4).items_center()
      .child(h_flex().id("tab-strip").flex_1().min_w(0).gap(4).items_center().overflow_x_scrollbar().children(tabs)
        .child(word(t, "tab-new", " + ", () => run("tab.new"))))
      .when(Boolean(w?.buttons), (el) => el
        .child(word(t, "win-min", " − ", () => run("window.minimize")))
        .child(word(t, "win-max", " □ ", () => run("window.maximize")))
        .child(word(t, "win-close", " × ", () => run("window.close"))));
  }

  // The label the TUI writes on a pane's top border.
  paneLabel(t, id) {
    const p = panes().find((x) => x.pane === id);
    if (!p) return div();
    const name = p.name || (p.program?.agent ? p.program.name : p.title) || p.program?.name || "shell";
    return h_flex().id(`pane-label-${id}`).size_full().px(8).gap(8).items_center().bg(t.background).text_size(12)
      .on_click(() => run("pane.focus", { pane: id }))
      .on_mouse_down("right", () => menu("pane", { pane: id, terminal: p.terminal }))
      .child(div().min_w(0).truncate().text_color(p.focused ? t.accent : t.foreground)
        .when(p.focused, (el) => el.font_bold()).child(name))
      .when(Boolean(p.status), (el) => el.child(div().flex_none().text_color(t[p.status] ?? t.dim).child(p.status ?? "")))
      .when(Boolean(p.zoomed), (el) => el.child(div().flex_none().text_color(t.dim).child("zoom")));
  }

  render() {
    const t = theme();
    const { part, pane } = props() ?? {};
    if (pane) return this.paneLabel(t, pane);
    const body = part === "agents" ? this.agentsPart(t) : part === "tabs" ? this.tabsPart(t) : this.spacesPart(t);
    return div().size_full().min_h(0).bg(t.chrome).text_size(SIZE).text_color(t.foreground).child(body);
  }
}
