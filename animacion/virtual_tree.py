import os
import json
from manim import *

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

def load_log(name):
    path = os.path.join(LOGS_DIR, f"vt_log_{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class VirtualTreeScene(Scene):
    def construct(self):
        # 0. Audio opcional
        audio_path = os.path.join(AUDIO_DIR, "narracion_completa.m4a")
        if os.path.exists(audio_path):
            self.add_sound(audio_path)

        # 1. Portada con Título e Integrantes
        self.title_screen()

        # 2. Introducción dividida en pantallas claras
        # 2.1 Pantalla de TDA y Gráfico representativo
        self.intro_tda_screen()

        # 2.2 Pantalla de Propósito, Aplicaciones y Propiedad clave
        self.intro_purpose_screen()

        # 2.3 Pantalla de Algoritmo en 3 Pasos
        self.intro_algorithm_screen()

        # 3. Demostración Principal (k = 4) con ritmo pausado
        main_log = load_log("main")
        if main_log:
            self.demo_scene(main_log, "Demostración: k = 4 nodos clave", speed=1.0, fast=False)

        # 4. Casos Borde Relevantes
        single_log = load_log("single")
        if single_log:
            self.demo_scene(single_log, "Caso Borde 1: k = 1 (Un solo nodo clave)", speed=0.7, fast=False)

        chain_log = load_log("chain")
        if chain_log:
            self.demo_scene(chain_log, "Caso Borde 2: Claves en cadena (Ancestros directos)", speed=0.7, fast=False)

        worstcase_log = load_log("worstcase")
        if worstcase_log:
            self.demo_scene(worstcase_log, "Peor Caso: Todos los nodos son clave (k = N)", speed=0.2, fast=True)

        # 5. Análisis de Complejidad Temporal y Espacial
        self.complexity_screen()

        # 6. Créditos Finales
        self.credits_screen()

    # ==========================================
    # 1. PANTALLA DE TÍTULO
    # ==========================================
    def title_screen(self):
        title = Text("Árbol Virtual", font_size=52, color=YELLOW, weight=BOLD)
        subtitle = Text("Virtual Tree / Auxiliary Tree", font_size=28, color=BLUE_B)
        course = Text("Estructuras de Datos y Algoritmos Avanzados", font_size=22, color=GRAY_A)

        authors_box = VGroup(
            Text("Integrantes:", font_size=24, color=WHITE, weight=BOLD),
            Text("• Fabiana Antonella Ameri Ingaruca", font_size=24, color=YELLOW_B),
            Text("• Joaquin Emilio Justo Guillen", font_size=24, color=YELLOW_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        content = VGroup(title, subtitle, course, authors_box).arrange(DOWN, buff=0.45)
        
        self.play(FadeIn(title, shift=DOWN), FadeIn(subtitle))
        self.play(FadeIn(course), FadeIn(authors_box, shift=UP))
        self.wait(2.5)
        self.play(FadeOut(content))

    # ==========================================
    # 2.1 INTRODUCCIÓN: TDA Y GRÁFICO REPRESENTATIVO
    # ==========================================
    def intro_tda_screen(self):
        head = Text("¿Qué es un Árbol Virtual? (Virtual Tree)", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.45)

        tda_box = RoundedRectangle(corner_radius=0.15, height=1.1, width=12.2, color=BLUE_D, fill_color=BLUE_E, fill_opacity=0.35)
        tda_text = VGroup(
            Text("Tipo de Dato Abstracto (TDA): Árbol Enraizado (Compressed Tree)", font_size=21, color=WHITE, weight=BOLD),
            Text("Grafo conexo y acíclico que retiene únicamente k nodos clave y sus ancestros comunes (LCA),", font_size=17, color=GRAY_A),
            Text("preservando las relaciones de ancestro y distancias relativas del árbol original.", font_size=17, color=GRAY_A)
        ).arrange(DOWN, buff=0.08).move_to(tda_box)
        tda_group = VGroup(tda_box, tda_text).next_to(head, DOWN, buff=0.25)

        # Gráfico representativo: Árbol Original -> Comprimir -> Árbol Virtual
        # Lado Izquierdo: Árbol Original (7 nodos, 3 clave)
        left_nodes_pos = {
            0: [-4.2, 0.4, 0],
            1: [-5.1, -0.5, 0],
            2: [-3.3, -0.5, 0],
            3: [-5.6, -1.5, 0],
            4: [-4.6, -1.5, 0],
            5: [-3.8, -1.5, 0],
            6: [-2.8, -1.5, 0]
        }
        orig_edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        key_nodes_set = {3, 4, 5}

        orig_edges_mobs = VGroup(*[
            Line(left_nodes_pos[u], left_nodes_pos[v], color=GRAY_D, stroke_width=2.0)
            for u, v in orig_edges
        ])

        orig_nodes_mobs = VGroup()
        for u, pos in left_nodes_pos.items():
            is_k = u in key_nodes_set
            c = Circle(radius=0.22, color=YELLOW if is_k else GRAY_B, fill_color=YELLOW_D if is_k else GRAY_E, fill_opacity=0.9, stroke_width=2)
            c.move_to(pos)
            lbl = Text(str(u), font_size=14, color=BLACK if is_k else WHITE, weight=BOLD).move_to(pos)
            orig_nodes_mobs.add(VGroup(c, lbl))

        lbl_orig = Text("Árbol Original (N = 7, k = 3)", font_size=17, color=GRAY_A).next_to(orig_edges_mobs, DOWN, buff=0.55)
        left_group = VGroup(orig_edges_mobs, orig_nodes_mobs, lbl_orig)

        # Centro: Flecha de compresión
        arrow = Arrow(start=[-1.8, -0.5, 0], end=[0.8, -0.5, 0], color=YELLOW, buff=0.1, stroke_width=4.0)
        arrow_lbl = Text("Comprimir a\nk claves + LCA", font_size=16, color=YELLOW_A, weight=BOLD).next_to(arrow, UP, buff=0.12)
        center_group = VGroup(arrow, arrow_lbl)

        # Lado Derecho: Árbol Virtual Comprimido (solo 0, 1, 3, 4, 5)
        right_nodes_pos = {
            0: [3.3, 0.4, 0],
            1: [2.5, -0.5, 0],
            3: [2.0, -1.5, 0],
            4: [2.9, -1.5, 0],
            5: [4.1, -1.5, 0]
        }
        virt_edges = [(0, 1), (0, 5), (1, 3), (1, 4)]
        virt_edges_mobs = VGroup(*[
            Line(right_nodes_pos[u], right_nodes_pos[v], color=ORANGE, stroke_width=3.8)
            for u, v in virt_edges
        ])

        virt_nodes_mobs = VGroup()
        for u, pos in right_nodes_pos.items():
            is_k = u in key_nodes_set
            c = Circle(radius=0.22, color=YELLOW if is_k else TEAL, fill_color=YELLOW_D if is_k else TEAL_E, fill_opacity=0.9, stroke_width=2.5)
            c.move_to(pos)
            lbl = Text(str(u), font_size=14, color=BLACK if is_k else WHITE, weight=BOLD).move_to(pos)
            virt_nodes_mobs.add(VGroup(c, lbl))

        lbl_virt = Text("Árbol Virtual (≤ 2k nodos)", font_size=17, color=ORANGE, weight=BOLD).next_to(virt_edges_mobs, DOWN, buff=0.55)
        right_group = VGroup(virt_edges_mobs, virt_nodes_mobs, lbl_virt)

        diag_group = VGroup(left_group, center_group, right_group)

        self.play(FadeIn(head))
        self.play(FadeIn(tda_group, shift=UP))
        self.play(FadeIn(left_group))
        self.play(GrowArrow(arrow), FadeIn(arrow_lbl))
        self.play(FadeIn(right_group))
        self.wait(5.0)
        self.play(FadeOut(head), FadeOut(tda_group), FadeOut(diag_group))

    # ==========================================
    # 2.2 INTRODUCCIÓN: PROPÓSITO, APLICACIONES Y PROPIEDAD CLAVE
    # ==========================================
    def intro_purpose_screen(self):
        head = Text("Propósito y Aplicaciones Prácticas", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.5)

        # Tarjeta 1: Propósito
        box1 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=BLUE_D, fill_color=BLACK, fill_opacity=0.5)
        t1 = VGroup(
            Text("• Propósito Principal:", font_size=20, color=YELLOW, weight=BOLD),
            Text("Responder consultas sobre subconjuntos de k nodos clave en tiempo O(k log k) u O(k),", font_size=18, color=WHITE),
            Text("evitando el costo O(N) de recorrer todo el árbol original cuando k << N.", font_size=18, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box1)
        card1 = VGroup(box1, t1)

        # Tarjeta 2: Aplicaciones Prácticas
        box2 = RoundedRectangle(corner_radius=0.15, height=1.65, width=12.2, color=TEAL_D, fill_color=BLACK, fill_opacity=0.5)
        t2 = VGroup(
            Text("• Aplicaciones en la Práctica:", font_size=20, color=TEAL_B, weight=BOLD),
            Text("1) Programación Dinámica en árboles (Tree DP sobre subconjuntos dinámicos).", font_size=18, color=WHITE),
            Text("2) Distancias y costos mínimos: Conectar k servidores o ciudades críticas.", font_size=18, color=WHITE),
            Text("3) Consultas frecuentes: Escenarios donde la suma de k_i sobre Q consultas es pequeña.", font_size=18, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box2)
        card2 = VGroup(box2, t2)

        # Tarjeta 3: Propiedad Clave
        box3 = RoundedRectangle(corner_radius=0.15, height=1.3, width=12.2, color=GREEN_D, fill_color=BLACK, fill_opacity=0.5)
        t3 = VGroup(
            Text("• Propiedad Estructural Clave:", font_size=20, color=GREEN_B, weight=BOLD),
            Text("Para cualquier subconjunto de k nodos, el árbol virtual tiene a lo sumo 2k - 1 nodos", font_size=18, color=WHITE),
            Text("(exactamente las k claves más a lo sumo k - 1 ancestros comunes LCA).", font_size=18, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(box3)
        card3 = VGroup(box3, t3)

        cards = VGroup(card1, card2, card3).arrange(DOWN, buff=0.28).next_to(head, DOWN, buff=0.35)

        self.play(FadeIn(head))
        self.play(LaggedStart(FadeIn(card1, shift=RIGHT*0.2), FadeIn(card2, shift=RIGHT*0.2), FadeIn(card3, shift=RIGHT*0.2), lag_ratio=0.25))
        self.wait(5.5)
        self.play(FadeOut(head), FadeOut(cards))

    # ==========================================
    # 2.3 INTRODUCCIÓN: ALGORITMO EN 3 PASOS
    # ==========================================
    def intro_algorithm_screen(self):
        head = Text("Algoritmo de Construcción (en 3 Pasos)", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.5)

        # Paso 1
        b1 = RoundedRectangle(corner_radius=0.15, height=1.45, width=12.2, color=BLUE_D, fill_color=BLACK, fill_opacity=0.5)
        txt1 = VGroup(
            Text("Paso 1: Ordenar claves por Tiempo de Entrada DFS (tin)", font_size=20, color=BLUE_B, weight=BOLD),
            Text("Se realiza un DFS previo. Se ordenan los k nodos clave según tin[v].", font_size=18, color=WHITE),
            Text("Garantía: Los nodos se procesan rama por rama, recorriendo el árbol de izquierda a derecha.", font_size=17, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(b1)
        p1 = VGroup(b1, txt1)

        # Paso 2
        b2 = RoundedRectangle(corner_radius=0.15, height=1.45, width=12.2, color=ORANGE, fill_color=BLACK, fill_opacity=0.5)
        txt2 = VGroup(
            Text("Paso 2: Pila Activa (Stack)", font_size=20, color=ORANGE, weight=BOLD),
            Text("La pila almacena la rama activa actual (el camino desde la raíz hasta el último nodo).", font_size=18, color=WHITE),
            Text("Permite detectar cuándo cambiamos de subárbol y cuándo se debe cerrar una rama.", font_size=17, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(b2)
        p2 = VGroup(b2, txt2)

        # Paso 3
        b3 = RoundedRectangle(corner_radius=0.15, height=1.65, width=12.2, color=GREEN_D, fill_color=BLACK, fill_opacity=0.5)
        txt3 = VGroup(
            Text("Paso 3: Consulta LCA y Compresión de Ramas", font_size=20, color=GREEN_B, weight=BOLD),
            Text("Para cada nueva clave v, se calcula l = LCA(v, tope de la pila):", font_size=18, color=WHITE),
            Text("• Si el tope no es ancestro de v: se desapilan nodos y se unen con aristas virtuales hasta l.", font_size=17, color=GRAY_A),
            Text("• Se inserta el nodo l (si no estaba) y luego se apila la nueva clave v.", font_size=17, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to(b3)
        p3 = VGroup(b3, txt3)

        steps = VGroup(p1, p2, p3).arrange(DOWN, buff=0.25).next_to(head, DOWN, buff=0.35)

        self.play(FadeIn(head))
        self.play(LaggedStart(FadeIn(p1, shift=DOWN*0.15), FadeIn(p2, shift=DOWN*0.15), FadeIn(p3, shift=DOWN*0.15), lag_ratio=0.25))
        self.wait(5.5)
        self.play(FadeOut(head), FadeOut(steps))

    # ==========================================
    # 3. DEMOSTRACIÓN ANIMADA PASO A PASO
    # ==========================================
    def demo_scene(self, data, demo_title, speed=1.0, fast=False):
        tree_info = data["tree"]
        keys = data["keys"]
        depth = data.get("depth", [0] * tree_info["n"])
        events = data.get("events", [])

        # Encabezado
        title = Text(demo_title, font_size=26, color=YELLOW, weight=BOLD).to_edge(UP, buff=0.35)
        keys_info = Text(f"Claves (k = {len(keys)}): {keys}", font_size=19, color=BLUE_B).next_to(title, DOWN, buff=0.12)
        header = VGroup(title, keys_info)
        self.play(FadeIn(header), run_time=0.4)

        # Posiciones del árbol base (Lado Izquierdo: x in [-6.2, 0.6])
        pos = self.calc_tree_layout(tree_info, depth, x_range=(-6.2, 0.6), y_range=(1.8, -3.2))

        # Crear mobjects del árbol base
        base_edges = VGroup()
        for u, v in tree_info["edges"]:
            line = Line(pos[u], pos[v], color=GRAY_D, stroke_width=2.0)
            base_edges.add(line)

        node_mobs = {}
        for u in range(tree_info["n"]):
            is_key = u in keys
            c_fill = YELLOW_D if is_key else GRAY_E
            c_stroke = YELLOW if is_key else GRAY_B
            r = 0.22 if not fast else 0.18
            circle = Circle(radius=r, color=c_stroke, fill_color=c_fill, fill_opacity=0.85, stroke_width=2.5)
            circle.move_to(pos[u])
            lbl = Text(str(u), font_size=15 if not fast else 12, color=BLACK if is_key else WHITE, weight=BOLD)
            lbl.move_to(pos[u])
            node_mobs[u] = VGroup(circle, lbl)

        tree_group = VGroup(base_edges, *[node_mobs[u] for u in range(tree_info["n"])])
        self.play(FadeIn(tree_group), run_time=0.6)

        # Panel Derecho: Pila y Estado (x in [1.8, 6.4])
        panel_box = RoundedRectangle(corner_radius=0.15, height=5.3, width=4.6, color=BLUE_D, fill_color=BLACK, fill_opacity=0.55)
        panel_box.move_to([4.1, -0.65, 0])
        panel_title = Text("Pila (Stack)", font_size=20, color=BLUE_B, weight=BOLD).next_to(panel_box.get_top(), DOWN, buff=0.2)
        status_label = Text("Paso a paso:", font_size=15, color=GRAY_A).next_to(panel_title, DOWN, buff=0.18)
        
        status_text = Text("Inicio de construcción", font_size=15, color=WHITE).next_to(status_label, DOWN, buff=0.12)
        stack_container = VGroup().next_to(status_text, DOWN, buff=0.25)
        panel_group = VGroup(panel_box, panel_title, status_label, status_text, stack_container)
        
        if not fast:
            self.play(FadeIn(panel_group), run_time=0.4)

        # Colección de aristas virtuales añadidas
        vt_edges = VGroup()
        stack_boxes = VGroup()

        def update_stack_ui(new_stack):
            new_boxes = VGroup()
            for idx, val in enumerate(new_stack):
                b = RoundedRectangle(corner_radius=0.1, height=0.42, width=2.8, color=GREEN if val in keys else TEAL, fill_color=BLACK, fill_opacity=0.75)
                t = Text(f"nodo {val}" + (" [clave]" if val in keys else " [LCA]"), font_size=14, color=WHITE)
                t.move_to(b)
                new_boxes.add(VGroup(b, t))
            new_boxes.arrange(UP, buff=0.1).next_to(status_text, DOWN, buff=0.25)
            return new_boxes

        # Paso más lento y cómodo para el usuario
        step_dt = 0.9 * speed if not fast else 0.12 * speed
        for ev in events:
            t = ev.get("t", "")
            a, b, c = ev.get("a", -1), ev.get("b", -1), ev.get("c", -1)
            st = ev.get("stack", [])

            if t == "sort":
                txt = "Claves ordenadas por tin"
            elif t == "start":
                txt = f"Apilar raíz {a}"
            elif t == "visit":
                txt = f"Procesar clave {a}"
            elif t == "lca":
                txt = f"LCA({a}, tope={b}) = {c}"
            elif t == "edge":
                txt = f"Arista VT: {a} -> {b}"
                vt_edge = Line(pos[a], pos[b], color=ORANGE, stroke_width=4.5)
                vt_edges.add(vt_edge)
                if not fast:
                    self.play(Create(vt_edge), run_time=0.5 * speed)
                else:
                    self.add(vt_edge)
                if a not in keys and a in node_mobs:
                    node_mobs[a][0].set_color(TEAL).set_fill(TEAL_E, opacity=0.9)
                    node_mobs[a][1].set_color(WHITE)
            elif t == "push":
                txt = f"Push({a}) a la pila"
            elif t == "pop":
                txt = f"Pop({a}) de la pila"
            elif t == "replace":
                txt = f"Reemplazar {a} por LCA {b}"
            elif t == "finish":
                txt = "Construcción completada"
            else:
                txt = t

            if not fast:
                new_status = Text(txt, font_size=15, color=YELLOW_A if t in ["edge", "lca"] else WHITE).move_to(status_text)
                new_boxes = update_stack_ui(st)
                self.remove(status_text, stack_boxes)
                status_text = new_status
                stack_boxes = new_boxes
                self.add(status_text, stack_boxes)
                self.wait(step_dt)

        # Destacar resultado final sin overlapping
        if not fast:
            done_card = VGroup(
                RoundedRectangle(corner_radius=0.1, height=0.48, width=3.4, color=GREEN_B, fill_color=GREEN_E, fill_opacity=0.45),
                Text("✓ Construcción completada", font_size=15, color=WHITE, weight=BOLD)
            )
            done_card[1].move_to(done_card[0])
            done_card.move_to(status_text)
            self.play(Transform(status_text, done_card[1]), FadeIn(done_card[0]), run_time=0.4)

        # Resaltado visual en el árbol
        self.play(vt_edges.animate.set_stroke(color=YELLOW, width=5.5), run_time=0.4)
        self.play(vt_edges.animate.set_stroke(color=ORANGE, width=4.5), run_time=0.4)
        self.wait(1.5 if not fast else 0.8)

        # Limpiar escena sin colisiones
        all_mobs = [header, tree_group, vt_edges]
        if not fast:
            all_mobs.extend([panel_group, stack_boxes, done_card[0]])
        self.play(FadeOut(VGroup(*all_mobs)), run_time=0.5)

    # ==========================================
    # 4. ANÁLISIS DE COMPLEJIDAD
    # ==========================================
    def complexity_screen(self):
        head = Text("Análisis de Complejidad Temporal y Espacial", font_size=32, color=YELLOW, weight=BOLD)
        head.to_edge(UP, buff=0.6)

        table_data = [
            ("Fase / Operación", "Complejidad Temporal", "Explicación"),
            ("Preprocesamiento", "O(N log N) o O(N)", "DFS para tin/tout y estructura LCA (Sparse/Lifting)."),
            ("Ordenamiento", "O(k log k)", "Ordenar los k nodos clave según tin."),
            ("Construcción del VT", "O(k)", "A lo sumo 2k operaciones de pila y consultas LCA O(1)."),
            ("Consultas / DP sobre VT", "O(k)", "Se recorren solo los nodos del árbol virtual (≤ 2k)."),
            ("Espacio adicional", "O(k)", "Almacena a lo sumo 2k - 1 nodos y aristas."),
        ]

        col_x = [-6.0, -2.4, 0.4]
        y_start = 1.9
        y_step = 0.55

        rows = VGroup()
        for i, (col1, col2, col3) in enumerate(table_data):
            is_head = (i == 0)
            c1 = Text(col1, font_size=18 if is_head else 17, color=YELLOW if is_head else WHITE, weight=BOLD if is_head else NORMAL)
            c2 = Text(col2, font_size=18 if is_head else 17, color=YELLOW if is_head else GREEN_B, weight=BOLD)
            c3 = Text(col3, font_size=18 if is_head else 16, color=YELLOW if is_head else GRAY_A)
            
            y = y_start - i * y_step
            c1.move_to([col_x[0], y, 0], aligned_edge=LEFT)
            c2.move_to([col_x[1], y, 0], aligned_edge=LEFT)
            c3.move_to([col_x[2], y, 0], aligned_edge=LEFT)
            row = VGroup(c1, c2, c3)
            rows.add(row)

        conclusion_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=12.2, color=GREEN_D, fill_color=GREEN_E, fill_opacity=0.25)
        conclusion_txt = Text(
            "Conclusión: Si se realizan Q consultas con k << N, el tiempo total pasa de O(Q · N) a O(Q · k log k),\n"
            "haciendo el algoritmo óptimo para problemas de programación competitiva e índices en grafos.",
            font_size=18, color=WHITE
        ).move_to(conclusion_box)
        conclusion = VGroup(conclusion_box, conclusion_txt).next_to(rows, DOWN, buff=0.4)

        self.play(FadeIn(head))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT*0.2) for r in rows], lag_ratio=0.12))
        self.play(FadeIn(conclusion, shift=UP))
        self.wait(6.5)
        self.play(FadeOut(head), FadeOut(rows), FadeOut(conclusion))

    # ==========================================
    # 5. CRÉDITOS FINALES
    # ==========================================
    def credits_screen(self):
        title = Text("¡Gracias por su atención!", font_size=42, color=YELLOW, weight=BOLD)
        subtitle = Text("Proyecto Educativo: Árbol Virtual (Virtual Tree)", font_size=24, color=BLUE_B)

        authors_title = Text("Realizado por:", font_size=22, color=WHITE, weight=BOLD)
        a1 = Text("Fabiana Antonella Ameri Ingaruca", font_size=26, color=YELLOW_A)
        a2 = Text("Joaquin Emilio Justo Guillen", font_size=26, color=YELLOW_A)

        authors = VGroup(authors_title, a1, a2).arrange(DOWN, buff=0.2)
        credits_group = VGroup(title, subtitle, authors).arrange(DOWN, buff=0.5)

        self.play(FadeIn(title, shift=DOWN), FadeIn(subtitle))
        self.play(FadeIn(authors, shift=UP))
        self.wait(3.0)
        self.play(FadeOut(credits_group))

    # ==========================================
    # UTILIDAD: CÁLCULO DE COORDENADAS JERÁRQUICAS
    # ==========================================
    def calc_tree_layout(self, tree_info, depth, x_range=(-6.2, 0.6), y_range=(1.8, -3.2)):
        n = tree_info["n"]
        root = tree_info["root"]
        adj = [[] for _ in range(n)]
        for u, v in tree_info["edges"]:
            adj[u].append(v)

        order = []
        def get_leaves(u):
            if not adj[u]:
                order.append(u)
                return
            for v in adj[u]:
                get_leaves(v)

        get_leaves(root)
        pos = {}
        leaf_step = (x_range[1] - x_range[0]) / max(1, len(order) - 1)
        for idx, u in enumerate(order):
            pos[u] = [x_range[0] + idx * leaf_step, 0.0, 0.0]

        def assign_x(u):
            if not adj[u]:
                return pos[u][0]
            xs = [assign_x(v) for v in adj[u]]
            avg_x = sum(xs) / len(xs)
            pos[u] = [avg_x, 0.0, 0.0]
            return avg_x

        assign_x(root)
        max_d = max(depth) if max(depth) > 0 else 1
        y_step = (y_range[0] - y_range[1]) / max_d
        for u in range(n):
            y = y_range[0] - depth[u] * y_step
            pos[u] = [pos[u][0], y, 0.0]
        return pos
