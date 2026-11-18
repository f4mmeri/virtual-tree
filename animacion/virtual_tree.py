import os
import json
import numpy as np
from manim import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

PANEL_X = 4.1
STATUS_POS = np.array([PANEL_X, 0.75, 0.0])
ORDER_POS = np.array([PANEL_X, 1.25, 0.0])
STACK_BASE_Y = -3.0


def load_log(name):
    path = os.path.join(LOGS_DIR, f"vt_log_{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def first_event(log, op):
    return next(e for e in log["events"] if e["op"] == op)


def tin_of(log):
    return {e["v"]: e["tin"] for e in log["events"] if e["op"] == "dfs_enter"}


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


def node_size(gap):
    r = max(0.12, min(0.22, 0.42 * gap))
    font = max(9, int(round(15 * r / 0.22)))
    return r, font


def style_for(kind):
    if kind == "key":
        return YELLOW, YELLOW_D, BLACK
    if kind == "lca":
        return TEAL, TEAL_E, WHITE
    return GRAY_B, GRAY_E, WHITE


def make_node(label, position, kind, r, font):
    stroke, fill, txt = style_for(kind)
    circle = Circle(radius=r, color=stroke, fill_color=fill, fill_opacity=0.9, stroke_width=2.5)
    circle.move_to(position)
    lbl = Text(str(label), font_size=font, color=txt, weight=BOLD)
    lbl.move_to(position)
    group = VGroup(circle, lbl)
    group.set_z_index(3)
    return group


def paint_node(node, kind):
    stroke, fill, txt = style_for(kind)
    node[0].set_color(stroke)
    node[0].set_fill(fill, opacity=0.9)
    node[1].set_color(txt)


class VirtualTreeScene(Scene):
    def construct(self):
        audio_path = os.path.join(AUDIO_DIR, "narracion_completa.m4a")
        if os.path.exists(audio_path):
            self.add_sound(audio_path)

        main_log = load_log("main")
        edge_log = load_log("edge")
        single_log = load_log("single")

        self.title_screen()

        if main_log:
            self.intro_tda_screen(main_log)
        self.intro_purpose_screen()
        self.intro_algorithm_screen()

        if main_log:
            k = len(set(first_event(main_log, "query")["keys"]))
            self.demo_scene(main_log, f"Demostración: k = {k} nodos clave", speed=1.0, show_dfs=True)
        if edge_log:
            self.demo_scene(edge_log, "Caso borde: árbol en cadena, ningún LCA nuevo", speed=0.7)
        if single_log:
            self.demo_scene(single_log, "Caso borde: k = 1", speed=0.9)

        self.complexity_screen()
        self.credits_screen()

    def title_screen(self):
        title = Text("Árbol Virtual", font_size=52, color=YELLOW, weight=BOLD)
        subtitle = Text("Virtual Tree / Auxiliary Tree", font_size=28, color=BLUE_B)
        course = Text("CS2023 · Algoritmos y Estructuras de Datos · UTEC", font_size=22, color=GRAY_A)

        authors_box = VGroup(
            Text("Integrantes:", font_size=24, color=WHITE, weight=BOLD),
            Text("• Fabiana Antonella Ameri Ingaruca", font_size=24, color=YELLOW_B),
            Text("• Joaquin Emilio Justo Guillen", font_size=24, color=YELLOW_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        content = VGroup(title, subtitle, course, authors_box).arrange(DOWN, buff=0.45)

        self.play(FadeIn(title, shift=DOWN), FadeIn(subtitle), run_time=1)
        self.play(FadeIn(course), FadeIn(authors_box, shift=UP), run_time=1)
        self.wait(2.5)
        self.play(FadeOut(content), run_time=1)

    def intro_tda_screen(self, log):
        init = first_event(log, "init_tree")
        query = first_event(log, "query")
        result = first_event(log, "result")
        tin = tin_of(log)
        keys = set(query["keys"])

        head = Text("¿Qué es un Árbol Virtual?", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.45)

        tda_box = RoundedRectangle(corner_radius=0.15, height=1.1, width=12.2, color=BLUE_D, fill_color=BLUE_E, fill_opacity=0.35)
        tda_text = VGroup(
            Text("TDA: Árbol enraizado estático", font_size=21, color=WHITE, weight=BOLD),
            Text("Se construye a partir de un árbol original y de k nodos clave.", font_size=17, color=GRAY_A),
            Text("Conserva las claves y los ancestros comunes (LCA) que mantienen sus relaciones de ancestro.", font_size=17, color=GRAY_A),
        ).arrange(DOWN, buff=0.08).move_to(tda_box)
        tda_group = VGroup(tda_box, tda_text).next_to(head, DOWN, buff=0.25)

        left_pos, left_gap = tree_layout(init["root"], init["edges"], tin, (-6.3, -1.6), (0.5, -2.0))
        left_r, left_font = node_size(left_gap)
        left_edges = VGroup(*[
            Line(left_pos[p], left_pos[c], color=GRAY_D, stroke_width=2.0) for p, c in init["edges"]
        ])
        left_nodes = VGroup(*[
            make_node(v, left_pos[v], "key" if v in keys else "plain", left_r, left_font) for v in left_pos
        ])
        lbl_orig = Text(f"Árbol original (n = {init['n']}, k = {len(keys)})", font_size=17, color=GRAY_A)
        lbl_orig.move_to(np.array([-3.95, -2.75, 0.0]))
        left_group = VGroup(left_edges, left_nodes, lbl_orig)

        arrow = Arrow(start=np.array([-1.1, -0.8, 0.0]), end=np.array([1.1, -0.8, 0.0]), color=YELLOW, buff=0.05, stroke_width=4.0)
        arrow_lbl = Text("claves + LCA", font_size=16, color=YELLOW_A, weight=BOLD).next_to(arrow, UP, buff=0.12)

        right_pos, right_gap = tree_layout(result["root"], result["edges"], tin, (1.6, 6.3), (0.5, -2.0))
        right_r, right_font = node_size(right_gap)
        right_edges = VGroup(*[
            Line(right_pos[p], right_pos[c], color=ORANGE, stroke_width=3.8) for p, c in result["edges"]
        ])
        right_nodes = VGroup(*[
            make_node(v, right_pos[v], "key" if v in keys else "lca", right_r, right_font) for v in right_pos
        ])
        lbl_virt = Text("Árbol virtual (a lo más 2k − 1 nodos)", font_size=17, color=ORANGE, weight=BOLD)
        lbl_virt.move_to(np.array([3.95, -2.75, 0.0]))
        right_group = VGroup(right_edges, right_nodes, lbl_virt)

        self.play(FadeIn(head), run_time=1)
        self.play(FadeIn(tda_group, shift=UP), run_time=1)
        self.play(FadeIn(left_group), run_time=1)
        self.play(GrowArrow(arrow), FadeIn(arrow_lbl), run_time=1)
        self.play(FadeIn(right_group), run_time=1)
        self.wait(5.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)

    def intro_purpose_screen(self):
        head = Text("Propósito y aplicaciones", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.5)

        box1 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=BLUE_D, fill_color=BLACK, fill_opacity=0.5)
        t1 = VGroup(
            Text("• Propósito:", font_size=20, color=YELLOW, weight=BOLD),
            Text("Responder consultas sobre k nodos clave de un árbol fijo, sin recorrer los n nodos.", font_size=18, color=WHITE),
            Text("Útil cuando hay muchas consultas y k es mucho menor que n.", font_size=18, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box1)
        card1 = VGroup(box1, t1)

        box2 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=TEAL_D, fill_color=BLACK, fill_opacity=0.5)
        t2 = VGroup(
            Text("• En la práctica:", font_size=20, color=TEAL_B, weight=BOLD),
            Text("Programación dinámica sobre árboles, una consulta a la vez, sobre el árbol virtual.", font_size=18, color=WHITE),
            Text("Por ejemplo, el problema 613D de Codeforces.", font_size=18, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box2)
        card2 = VGroup(box2, t2)

        box3 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=GREEN_D, fill_color=BLACK, fill_opacity=0.5)
        t3 = VGroup(
            Text("• Propiedad clave:", font_size=20, color=GREEN_B, weight=BOLD),
            Text("Con k nodos clave, el árbol virtual tiene a lo más 2k − 1 nodos.", font_size=18, color=WHITE),
            Text("Los nodos extra son LCA donde se juntan al menos dos ramas.", font_size=18, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box3)
        card3 = VGroup(box3, t3)

        cards = VGroup(card1, card2, card3).arrange(DOWN, buff=0.28).next_to(head, DOWN, buff=0.35)

        self.play(FadeIn(head), run_time=1)
        self.play(LaggedStart(FadeIn(card1, shift=RIGHT * 0.2), FadeIn(card2, shift=RIGHT * 0.2), FadeIn(card3, shift=RIGHT * 0.2), lag_ratio=0.25))
        self.wait(5.5)
        self.play(FadeOut(head), FadeOut(cards), run_time=1)

    def intro_algorithm_screen(self):
        head = Text("Construcción en 3 pasos", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.5)

        b1 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=BLUE_D, fill_color=BLACK, fill_opacity=0.5)
        txt1 = VGroup(
            Text("Paso 1: ordenar las claves por tiempo de entrada (tin)", font_size=20, color=BLUE_B, weight=BOLD),
            Text("Un DFS previo calcula tin y tout. Las claves se recorren rama por rama.", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(b1)
        p1 = VGroup(b1, txt1)

        b2 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=ORANGE, fill_color=BLACK, fill_opacity=0.5)
        txt2 = VGroup(
            Text("Paso 2: mantener una pila con la rama activa", font_size=20, color=ORANGE, weight=BOLD),
            Text("Guarda el camino desde la primera clave hasta la última visitada.", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(b2)
        p2 = VGroup(b2, txt2)

        b3 = RoundedRectangle(corner_radius=0.15, height=1.5, width=12.2, color=GREEN_D, fill_color=BLACK, fill_opacity=0.5)
        txt3 = VGroup(
            Text("Paso 3: calcular el LCA con el tope de la pila", font_size=20, color=GREEN_B, weight=BOLD),
            Text("Si el tope no es ancestro de la nueva clave, se desapilan nodos y se unen con aristas.", font_size=18, color=WHITE),
            Text("Si el LCA no estaba, se apila; luego se apila la nueva clave.", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(b3)
        p3 = VGroup(b3, txt3)

        steps = VGroup(p1, p2, p3).arrange(DOWN, buff=0.25).next_to(head, DOWN, buff=0.35)

        self.play(FadeIn(head), run_time=1)
        self.play(LaggedStart(FadeIn(p1, shift=DOWN * 0.15), FadeIn(p2, shift=DOWN * 0.15), FadeIn(p3, shift=DOWN * 0.15), lag_ratio=0.25))
        self.wait(5.5)
        self.play(FadeOut(head), FadeOut(steps), run_time=1)

    def demo_scene(self, log, demo_title, speed=1.0, show_dfs=False):
        events = log["events"]
        init = first_event(log, "init_tree")
        query = first_event(log, "query")
        result = first_event(log, "result")
        root, edges = init["root"], init["edges"]
        tin = tin_of(log)
        keys_given = query["keys"]
        keys = set(keys_given)
        result_nodes = set(result["nodes"])
        dt = 0.9 * speed

        title = Text(demo_title, font_size=26, color=YELLOW, weight=BOLD).to_edge(UP, buff=0.35)
        keys_info = Text(f"Claves (k = {len(keys)}): {keys_given}", font_size=19, color=BLUE_B).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(keys_info), run_time=0.4)

        pos, gap = tree_layout(root, edges, tin, (-6.2, 0.6), (1.8, -3.2))
        r, font = node_size(gap)

        base_edges = VGroup(*[Line(pos[p], pos[c], color=GRAY_D, stroke_width=2.0) for p, c in edges])
        node_mobs = {v: make_node(v, pos[v], "plain", r, font) for v in pos}
        self.play(FadeIn(base_edges), *[FadeIn(m) for m in node_mobs.values()], run_time=0.6)

        panel_box = RoundedRectangle(corner_radius=0.15, height=5.3, width=4.6, color=BLUE_D, fill_color=BLACK, fill_opacity=0.55)
        panel_box.move_to(np.array([PANEL_X, -0.65, 0.0]))
        panel_title = Text("Pila (Stack)", font_size=20, color=BLUE_B, weight=BOLD).move_to(np.array([PANEL_X, 1.75, 0.0]))
        self.play(FadeIn(panel_box), FadeIn(panel_title), run_time=0.4)

        state = {"status": None, "order": None, "stack": None}
        tin_labels = {}
        vt_edges = []

        def set_status(text, color=WHITE):
            new = Text(text, font_size=15, color=color).move_to(STATUS_POS)
            if state["status"] is not None:
                self.remove(state["status"])
            self.add(new)
            state["status"] = new

        def set_order(values):
            new = Text("Orden por tin: " + ", ".join(str(v) for v in values), font_size=14, color=BLUE_B).move_to(ORDER_POS)
            if state["order"] is not None:
                self.remove(state["order"])
            self.add(new)
            state["order"] = new

        def set_stack(values):
            if state["stack"] is not None:
                self.remove(state["stack"])
            boxes = VGroup()
            for val in values:
                is_key = val in keys
                box = RoundedRectangle(corner_radius=0.1, height=0.42, width=2.8, color=GREEN if is_key else TEAL, fill_color=BLACK, fill_opacity=0.75)
                label = Text(f"nodo {val}" + (" [clave]" if is_key else " [LCA]"), font_size=14, color=WHITE)
                label.move_to(box)
                boxes.add(VGroup(box, label))
            if len(values) > 0:
                boxes.arrange(UP, buff=0.1)
                boxes.shift(np.array([PANEL_X - boxes.get_center()[0], STACK_BASE_Y - boxes.get_bottom()[1], 0.0]))
            if len(values) > 0:
                self.add(boxes)
            state["stack"] = boxes

        set_status("Árbol original listo")
        set_stack([])
        self.wait(dt)

        for ev in events:
            op = ev["op"]

            if op == "dfs_enter":
                if not show_dfs:
                    continue
                v = ev["v"]
                set_status(f"DFS: entrar a {v} (tin = {ev['tin']})")
                lbl = Text(str(ev["tin"]), font_size=12, color=GRAY_A).next_to(node_mobs[v], RIGHT, buff=0.04)
                lbl.set_z_index(4)
                self.add(lbl)
                tin_labels[v] = lbl
                self.wait(0.15)

            elif op == "dfs_exit":
                if not show_dfs:
                    continue
                v = ev["v"]
                set_status(f"DFS: salir de {v} (tout = {ev['tout']})")
                self.remove(tin_labels[v])
                lbl = Text(f"{tin[v]}/{ev['tout']}", font_size=12, color=GRAY_A).next_to(node_mobs[v], RIGHT, buff=0.04)
                lbl.set_z_index(4)
                self.add(lbl)
                tin_labels[v] = lbl
                self.wait(0.15)

            elif op == "query":
                for v in keys:
                    paint_node(node_mobs[v], "key")
                set_status("Marcar los nodos clave", YELLOW_A)
                self.play(*[Indicate(node_mobs[v]) for v in keys], run_time=0.8)
                self.wait(dt)

            elif op == "sort":
                set_order(ev["after"])
                set_status("Ordenar las claves por tin")
                self.wait(dt)

            elif op == "lca":
                a, b, l = ev["a"], ev["b"], ev["result"]
                text = f"LCA({a}, {b}) = {l}"
                if l == b:
                    text += " (tope = ancestro)"
                elif not ev["is_key"]:
                    text += " (nodo nuevo)"
                if not ev["is_key"]:
                    paint_node(node_mobs[l], "lca")
                set_status(text, YELLOW_A)
                self.wait(dt)

            elif op == "push":
                set_stack(ev["stack"])
                set_status(f"Apilar {ev['v']}")
                self.wait(dt)

            elif op == "pop":
                set_stack(ev["stack"])
                set_status(f"Desapilar {ev['v']}")
                self.wait(dt)

            elif op == "add_edge":
                p, c = ev["parent"], ev["child"]
                line = Line(pos[p], pos[c], color=ORANGE, stroke_width=4.5)
                line.set_z_index(1)
                vt_edges.append(line)
                set_status(f"Arista virtual {p} -> {c}", YELLOW_A)
                self.play(Create(line), run_time=0.5 * speed)
                self.wait(dt)

            elif op == "result":
                set_status(f"Listo: {len(result['nodes'])} nodos y {len(result['edges'])} aristas", GREEN_B)
                dropped = [v for v in node_mobs if v not in result_nodes]
                fade = [node_mobs[v].animate.set_opacity(0.25) for v in dropped]
                if dropped:
                    fade.append(base_edges.animate.set_opacity(0.25))
                if fade:
                    self.play(*fade, run_time=0.8)
                pulse = [Indicate(node_mobs[v], color=ORANGE) for v in result_nodes]
                pulse += [ln.animate.set_stroke(color=YELLOW, width=5.5) for ln in vt_edges]
                self.play(*pulse, run_time=0.8)
                if vt_edges:
                    self.play(*[ln.animate.set_stroke(color=ORANGE, width=4.5) for ln in vt_edges], run_time=0.4)
                self.wait(1.5)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)

    def complexity_screen(self):
        head = Text("Análisis de complejidad", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.6)

        table_data = [
            ("Operación", "Complejidad", "Explicación"),
            ("DFS (tin, tout)", "O(n)", "Una sola vez sobre el árbol original."),
            ("Preparar el LCA", "O(n log n)", "Recorrido de Euler y sparse table."),
            ("LCA(u, v)", "O(1)", "Mínimo de profundidad en un rango."),
            ("Ordenar las k claves", "O(k log k)", "Por tiempo de entrada (tin)."),
            ("Construcción con pila", "O(k)", "Cada nodo entra y sale una vez."),
            ("Build(S) completo", "O(k log k)", "Domina el ordenamiento."),
        ]

        col_x = [-6.0, -2.4, 0.4]
        y_start = 1.9
        y_step = 0.55

        rows = VGroup()
        for i, (col1, col2, col3) in enumerate(table_data):
            is_head = i == 0
            c1 = Text(col1, font_size=18 if is_head else 17, color=YELLOW if is_head else WHITE, weight=BOLD if is_head else NORMAL)
            c2 = Text(col2, font_size=18 if is_head else 17, color=YELLOW if is_head else GREEN_B, weight=BOLD)
            c3 = Text(col3, font_size=18 if is_head else 16, color=YELLOW if is_head else GRAY_A)
            y = y_start - i * y_step
            c1.move_to(np.array([col_x[0], y, 0.0]), aligned_edge=LEFT)
            c2.move_to(np.array([col_x[1], y, 0.0]), aligned_edge=LEFT)
            c3.move_to(np.array([col_x[2], y, 0.0]), aligned_edge=LEFT)
            rows.add(VGroup(c1, c2, c3))

        conclusion_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=12.2, color=GREEN_D, fill_color=GREEN_E, fill_opacity=0.25)
        conclusion_txt = Text(
            "Con Q consultas y k mucho menor que n, el costo total pasa de O(Q · n)\n"
            "a O(n log n + Q · k log k).",
            font_size=18, color=WHITE,
        ).move_to(conclusion_box)
        conclusion = VGroup(conclusion_box, conclusion_txt).next_to(rows, DOWN, buff=0.4)

        self.play(FadeIn(head), run_time=1)
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.2) for row in rows], lag_ratio=0.12))
        self.play(FadeIn(conclusion, shift=UP), run_time=1)
        self.wait(6.5)
        self.play(FadeOut(head), FadeOut(rows), FadeOut(conclusion), run_time=1)

    def credits_screen(self):
        title = Text("¡Gracias por su atención!", font_size=42, color=YELLOW, weight=BOLD)
        subtitle = Text("Proyecto: Árbol Virtual (Virtual Tree)", font_size=24, color=BLUE_B)

        authors_title = Text("Realizado por:", font_size=22, color=WHITE, weight=BOLD)
        a1 = Text("Fabiana Antonella Ameri Ingaruca", font_size=26, color=YELLOW_A)
        a2 = Text("Joaquin Emilio Justo Guillen", font_size=26, color=YELLOW_A)

        authors = VGroup(authors_title, a1, a2).arrange(DOWN, buff=0.2)
        credits_group = VGroup(title, subtitle, authors).arrange(DOWN, buff=0.5)

        self.play(FadeIn(title, shift=DOWN), FadeIn(subtitle), run_time=1)
        self.play(FadeIn(authors, shift=UP), run_time=1)
        self.wait(3.0)
        self.play(FadeOut(credits_group), run_time=1)
