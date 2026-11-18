import json
import os

import numpy as np
from manim import *

PROJECT_TITLE = "Virtual Tree (Auxiliary Tree)"
MEMBERS = "Integrantes: Fabiana Ameri · Joaquín Justo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

WAIT = {
    "opening": 1,
    "concept": 10,
    "dfs": 6,
    "sort": 8,
    "stack": 4,
    "chain": 4,
    "complexity": 12,
}


def load_events(name):
    path = os.path.join(LOGS_DIR, f"vt_log_{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)["events"]


def first_event(events, op):
    return next(e for e in events if e["op"] == op)


def tin_map(events):
    return {e["v"]: e["tin"] for e in events if e["op"] == "dfs_enter"}


def tree_layout(root, edges, order, x_range, y_range):
    kids = {}
    for p, c in edges:
        kids.setdefault(p, []).append(c)
    for p in kids:
        kids[p].sort(key=lambda v: order[v])

    depth = {root: 0}
    leaves = []

    def walk(u):
        for v in kids.get(u, []):
            depth[v] = depth[u] + 1
            walk(v)
        if u not in kids:
            leaves.append(u)

    walk(root)

    if len(leaves) == 1 and len(depth) > 1:
        ordered = sorted(depth, key=lambda v: depth[v])
        step = (x_range[1] - x_range[0]) / (len(ordered) - 1)
        y = (y_range[0] + y_range[1]) / 2
        pos = {v: np.array([x_range[0] + i * step, y, 0.0]) for i, v in enumerate(ordered)}
        return pos, step

    xs = {}
    if len(leaves) == 1:
        step_x = None
        xs[leaves[0]] = (x_range[0] + x_range[1]) / 2
    else:
        step_x = (x_range[1] - x_range[0]) / (len(leaves) - 1)
        for i, u in enumerate(leaves):
            xs[u] = x_range[0] + i * step_x

    def assign(u):
        if u not in kids:
            return xs[u]
        vals = [assign(v) for v in kids[u]]
        xs[u] = sum(vals) / len(vals)
        return xs[u]

    assign(root)

    max_d = max(depth.values())
    step_y = (y_range[0] - y_range[1]) / max_d if max_d > 0 else None
    pos = {}
    for u, d in depth.items():
        y = y_range[0] - d * step_y if step_y is not None else (y_range[0] + y_range[1]) / 2
        pos[u] = np.array([xs[u], y, 0.0])

    gaps = [g for g in (step_x, step_y) if g is not None]
    gap = min(gaps) if gaps else 1.0
    return pos, gap


def node_style(gap):
    radius = min(0.34, 0.42 * gap)
    font = max(12, int(round(23 * radius / 0.34)))
    return radius, font


def make_node(label, point, color=BLUE_C, radius=0.34, font=23):
    circle = Circle(radius=radius, color=color, stroke_width=3)
    circle.set_fill(BLACK, opacity=1)
    circle.move_to(point)
    text = Text(str(label), font_size=font, color=WHITE).move_to(circle)
    group = VGroup(circle, text)
    group.set_z_index(2)
    return group


def paint(node, color):
    node[0].set_stroke(color=color, width=3)


def make_caption(lines):
    caption = VGroup(*[
        Text(line, font_size=21, color=WHITE)
        for line in lines
    ]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    max_width = config.frame_width - 0.8
    if caption.width > max_width:
        caption.scale_to_fit_width(max_width)
    caption.to_edge(DOWN, buff=0.24)
    return caption


def make_heading(text):
    return Text(text, font_size=32, color=TEAL_C).to_edge(UP, buff=0.3)


def build_tree(events, x_range, y_range, key_color=YELLOW):
    init = first_event(events, "init_tree")
    keys = set(first_event(events, "query")["keys"])
    pos, gap = tree_layout(init["root"], init["edges"], tin_map(events), x_range, y_range)
    radius, font = node_style(gap)
    edges = VGroup(*[Line(pos[p], pos[c], color=GRAY_B, stroke_width=2.5) for p, c in init["edges"]])
    nodes = {
        v: make_node(v, pos[v], key_color if v in keys else BLUE_C, radius, font)
        for v in pos
    }
    return pos, edges, nodes, keys


class VirtualTreeVideo(Scene):
    def construct(self):
        audio_path = os.path.join(AUDIO_DIR, "narracion_completa.m4a")
        if os.path.exists(audio_path):
            self.add_sound(audio_path)

        main = load_events("main")
        edge = load_events("edge")

        self.opening()
        self.concept(main)
        self.dfs_demo(main)
        self.sort_demo(main)
        self.stack_demo(
            main, "Paso 3: construcción con una pila", WAIT["stack"], step=0.9,
            x_range=(-5.5, 5.5), y_range=(2.2, -1.8),
        )
        self.stack_demo(
            edge, "Caso borde: claves en una cadena", WAIT["chain"], step=0.7,
            x_range=(-6.0, 6.0), y_range=(0.4, 0.4),
        )
        self.complexity_summary()
        self.credits()

    def opening(self):
        title = Text(PROJECT_TITLE, font_size=46, color=TEAL_C)
        subtitle = Text("Un árbol pequeño que resume un subconjunto de nodos", font_size=25)
        members = Text(MEMBERS, font_size=22, color=GRAY_A)
        group = VGroup(title, subtitle, members).arrange(DOWN, buff=0.38)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.15), FadeIn(members), run_time=1)
        self.wait(WAIT["opening"])
        self.play(FadeOut(group), run_time=1)

    def concept(self, events):
        heading = make_heading("¿Qué es un Virtual Tree?")
        caption = make_caption([
            "Es un árbol enraizado que se construye a partir de un árbol original y de k nodos clave.",
            "Conserva las claves y los ancestros comunes (LCA) que mantienen sus relaciones de ancestro.",
            "Sirve para responder consultas sobre pocos nodos de un árbol fijo, y tiene a lo más 2k − 1 nodos.",
        ])
        self.play(FadeIn(heading, shift=DOWN * 0.15), Write(caption), run_time=1)

        init = first_event(events, "init_tree")
        result = first_event(events, "result")
        keys = set(first_event(events, "query")["keys"])
        tin = tin_map(events)

        left_pos, left_gap = tree_layout(init["root"], init["edges"], tin, (-6.2, -1.4), (1.9, -0.5))
        left_r, left_font = node_style(left_gap)
        left_edges = VGroup(*[Line(left_pos[p], left_pos[c], color=GRAY_B, stroke_width=2.5) for p, c in init["edges"]])
        left_nodes = VGroup(*[
            make_node(v, left_pos[v], YELLOW if v in keys else BLUE_C, left_r, left_font) for v in left_pos
        ])
        left_label = Text("Árbol original", font_size=22, color=GRAY_A).move_to(np.array([-3.8, -1.25, 0.0]))

        right_pos, right_gap = tree_layout(result["root"], result["edges"], tin, (1.4, 6.2), (1.9, -0.5))
        right_r, right_font = node_style(right_gap)
        right_edges = VGroup(*[Line(right_pos[p], right_pos[c], color=ORANGE, stroke_width=3.5) for p, c in result["edges"]])
        right_nodes = VGroup(*[
            make_node(v, right_pos[v], YELLOW if v in keys else ORANGE, right_r, right_font) for v in right_pos
        ])
        right_label = Text("Virtual Tree", font_size=22, color=ORANGE).move_to(np.array([3.8, -1.25, 0.0]))

        arrow = Arrow(np.array([-1.0, 0.7, 0.0]), np.array([1.0, 0.7, 0.0]), buff=0.05, color=YELLOW, stroke_width=4)

        self.play(FadeIn(left_edges), LaggedStart(*[GrowFromCenter(n) for n in left_nodes], lag_ratio=0.1))
        self.play(FadeIn(left_label), run_time=1)
        self.play(GrowArrow(arrow), run_time=1)
        self.play(FadeIn(right_edges), LaggedStart(*[GrowFromCenter(n) for n in right_nodes], lag_ratio=0.15))
        self.play(FadeIn(right_label), run_time=1)
        self.wait(WAIT["concept"])
        self.play(FadeOut(VGroup(
            heading, caption, left_edges, left_nodes, left_label,
            right_edges, right_nodes, right_label, arrow,
        )))

    def dfs_demo(self, events):
        heading = make_heading("Paso 1: DFS con tin y tout")
        caption = make_caption([
            "Un DFS asigna a cada nodo su tiempo de entrada (tin) y de salida (tout).",
            "Se hace una sola vez sobre el árbol original y cuesta O(n).",
        ])
        pos, edges, nodes, keys = build_tree(events, (-5.5, 5.5), (2.2, -1.8), key_color=BLUE_C)
        tin = tin_map(events)

        self.play(FadeIn(heading), FadeIn(edges), LaggedStart(*[FadeIn(n) for n in nodes.values()], lag_ratio=0.08))
        self.play(Write(caption), run_time=1)

        labels = {}
        for ev in events:
            if ev["op"] == "dfs_enter":
                v = ev["v"]
                paint(nodes[v], YELLOW)
                lbl = Text(str(ev["tin"]), font_size=20, color=TEAL_C).next_to(nodes[v], RIGHT, buff=0.08)
                self.add(lbl)
                labels[v] = lbl
                self.wait(0.25)
            elif ev["op"] == "dfs_exit":
                v = ev["v"]
                paint(nodes[v], BLUE_C)
                self.remove(labels[v])
                lbl = Text(f"{tin[v]}/{ev['tout']}", font_size=20, color=TEAL_C).next_to(nodes[v], RIGHT, buff=0.08)
                self.add(lbl)
                labels[v] = lbl
                self.wait(0.25)

        self.wait(WAIT["dfs"])
        self.play(*[FadeOut(m) for m in self.mobjects])

    def sort_demo(self, events):
        heading = make_heading("Paso 2: ordenar las claves por tin")
        sort_ev = first_event(events, "sort")
        tin = tin_map(events)
        pos, edges, nodes, keys = build_tree(events, (-5.5, 5.5), (2.2, -1.8))

        caption = make_caption([
            f"Las claves {sort_ev['before']} se ordenan por tin: {sort_ev['after']}.",
            "Ordenar k claves cuesta O(k log k).",
        ])

        self.play(FadeIn(heading), FadeIn(edges), LaggedStart(*[FadeIn(n) for n in nodes.values()], lag_ratio=0.08))
        self.play(Write(caption), run_time=1)

        tin_labels = VGroup(*[
            Text(f"tin {tin[v]}", font_size=20, color=TEAL_C).next_to(nodes[v], DOWN, buff=0.1)
            for v in sort_ev["after"]
        ])
        self.play(LaggedStart(*[FadeIn(t) for t in tin_labels], lag_ratio=0.2))
        order_labels = VGroup(*[
            Text(str(i + 1), font_size=26, color=YELLOW).next_to(nodes[v], UP, buff=0.1)
            for i, v in enumerate(sort_ev["after"])
        ])
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.15) for t in order_labels], lag_ratio=0.5))
        self.wait(WAIT["sort"])
        self.play(*[FadeOut(m) for m in self.mobjects])

    def stack_demo(self, events, title, final_wait, step, x_range, y_range):
        heading = make_heading(title)
        pos, edges, nodes, keys = build_tree(events, x_range, y_range)
        result = first_event(events, "result")
        result_nodes = set(result["nodes"])
        k = len(keys)

        state = {"caption": None}

        def show_caption(lines, first=False):
            new = make_caption(lines)
            if first:
                self.play(Write(new), run_time=1)
            else:
                self.remove(state["caption"])
                self.add(new)
            state["caption"] = new

        self.play(FadeIn(heading), FadeIn(edges), LaggedStart(*[FadeIn(n) for n in nodes.values()], lag_ratio=0.08))
        show_caption(["Las claves están marcadas en amarillo.", "Pila: []"], first=True)
        self.wait(step)

        virtual_edges = []
        for ev in events:
            op = ev["op"]
            if op == "push":
                if ev["v"] not in keys:
                    paint(nodes[ev["v"]], ORANGE)
                show_caption([f"Apilar {ev['v']}.", f"Pila: {ev['stack']}"])
                self.wait(step)
            elif op == "pop":
                show_caption([f"Desapilar {ev['v']}.", f"Pila: {ev['stack']}"])
                self.wait(step)
            elif op == "lca":
                a, b, l = ev["a"], ev["b"], ev["result"]
                if l == b:
                    note = f"el tope {b} es ancestro de {a}, solo se apila {a}."
                elif ev["is_key"]:
                    note = f"{l} ya es una clave."
                else:
                    note = f"{l} es un nodo nuevo, no era clave."
                    paint(nodes[l], ORANGE)
                show_caption([f"LCA({a}, {b}) = {l}: {note}", f"Pila: {self.current_stack(events, ev)}"])
                self.wait(step)
            elif op == "add_edge":
                p, c = ev["parent"], ev["child"]
                line = Line(pos[p], pos[c], color=ORANGE, stroke_width=4.5)
                line.set_z_index(1)
                virtual_edges.append(line)
                show_caption([f"Arista virtual: {p} es el padre de {c}.", f"Pila: {self.current_stack(events, ev)}"])
                self.play(Create(line), run_time=0.5)
                self.wait(step)

        dropped = [v for v in nodes if v not in result_nodes]
        if dropped:
            self.play(
                *[nodes[v].animate.set_opacity(0.25) for v in dropped],
                edges.animate.set_opacity(0.25),
                run_time=1,
            )
        new = len(result["nodes"]) - k
        if k == 1:
            note = "Con una sola clave, el árbol virtual es ese nodo, sin aristas."
        elif new == 0:
            note = "Ninguna clave necesita un LCA nuevo: quedan solo las k claves."
        elif new == k - 1:
            note = f"Se agregaron {new} LCA: es el máximo, 2k − 1 = {len(result['nodes'])} nodos."
        else:
            note = f"Se agregaron {new} nodos LCA."
        show_caption([
            f"Resultado: {len(result['nodes'])} nodos y {len(result['edges'])} aristas.",
            note,
        ])
        self.wait(final_wait)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def current_stack(self, events, current):
        stack = []
        for ev in events:
            if ev is current:
                break
            if ev["op"] in ("push", "pop"):
                stack = ev["stack"]
        return stack

    def complexity_summary(self):
        heading = make_heading("Complejidad temporal")
        rows = [
            ["DFS (tin, tout)", "O(n)"],
            ["Preparar el LCA (Euler y sparse table)", "O(n log n)"],
            ["LCA(u, v)", "O(1)"],
            ["Ordenar las k claves por tin", "O(k log k)"],
            ["Construcción con pila", "O(k)"],
            ["Build(S) completo", "O(k log k)"],
        ]
        table = Table(
            rows,
            col_labels=[
                Text("Operación", font_size=24, color=TEAL_C),
                Text("Complejidad", font_size=24, color=TEAL_C),
            ],
            include_outer_lines=True,
            line_config={"stroke_color": WHITE, "stroke_width": 2.5},
            element_to_mobject=Text,
            element_to_mobject_config={"font_size": 22, "color": WHITE},
        )
        if table.width > config.frame_width - 1:
            table.scale_to_fit_width(config.frame_width - 1)
        table.next_to(heading, DOWN, buff=0.5)
        self.play(FadeIn(heading))
        self.play(LaggedStart(*[FadeIn(row) for row in table.get_rows()], lag_ratio=0.3))
        self.wait(WAIT["complexity"])
        self.play(FadeOut(VGroup(heading, table)))

    def credits(self):
        title = Text(PROJECT_TITLE, font_size=40, color=TEAL_C)
        members = Text(MEMBERS, font_size=24)
        credits = VGroup(title, members).arrange(DOWN, buff=0.4)
        self.play(FadeIn(credits, shift=UP * 0.2))