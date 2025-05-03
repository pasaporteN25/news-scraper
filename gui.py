import customtkinter as ctk
from tkinter import filedialog, messagebox
from main import scrape_all_sources
import asyncio
import threading
import webbrowser
from datetime import datetime
import os
import aiohttp
import json
import csv

class NewsScraperApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Global News Scraper Pro")
        self.root.geometry("1200x800")

        # Configuración de tema y apariencia
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Configura estilos SIN especificar fuente en los tags
        self.text_styles = {
            "header": {"foreground": "#2e8b57"},  # Solo color
            "param": {"foreground": "#666666"},
            "warning": {"foreground": "orange"},
            "hyperlink": {"foreground": "blue", "underline": True}
        }

        # Fuentes como atributos separados
        self.fonts = {
            "header": ("Helvetica", 12, "bold"),
            "param": ("Helvetica", 10, "italic"),
            "warning": ("Helvetica", 11, "italic"),
            "default": ("Consolas", 12)
        }

        self.hyperlink_behavior = {
            "enter": lambda e: None,
            "leave": lambda e: None
        }

        self.results_text = None
        self.results_frame = None
        self.articles = []
        self.favorites = []

        # --- INICIALIZACIÓN ---
        self.setup_ui()
        self._finalize_text_config()

    def _setup_text_styles(self):
        """Configura todos los estilos de texto"""
        self.text_styles = {
            # ... tus estilos aquí ...
        }

        if self.results_text:
            for tag_name, style in self.text_styles.items():
                self.results_text.tag_config(tag_name, **style)

            self.results_text.tag_bind("hyperlink", "<Enter>",
                                       lambda e: self.results_text.configure(cursor="hand2"))
            self.results_text.tag_bind("hyperlink", "<Leave>",
                                       lambda e: self.results_text.configure(cursor=""))

    def _finalize_text_config(self):
        """Configuración final del texto con soporte para CustomTkinter"""
        if self.results_text:
            # Configura la fuente base del Textbox
            self.results_text.configure(font=self.fonts["default"])

            # Aplica estilos sin la propiedad font
            for tag_name, style in self.text_styles.items():
                self.results_text.tag_config(tag_name, **style)

            # Configura comportamiento de hipervínculos
            self.results_text.tag_bind("hyperlink", "<Enter>",
                                       lambda e: self.results_text.configure(cursor="hand2"))
            self.results_text.tag_bind("hyperlink", "<Leave>",
                                       lambda e: self.results_text.configure(cursor=""))

    def setup_ui(self):
        # 1. Crear frames principales
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # 2. Crear sidebar
        self.create_sidebar()

        # 3. Crear área de resultados
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.pack(side="right", fill="both", expand=True, padx=5)

        # Configura primero el Textbox con la fuente deseada
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            font=("Helvetica", 12),  # Fuente base para todx el texto
            wrap="word",
            width=850,
            height=400,
            activate_scrollbars=True
        )
        self.results_text.pack(fill="both", expand=True)

        # Configura tags SIN especificar fuente
        self.results_text.tag_config("header", foreground="#2e8b57")  # Solo color
        self.results_text.tag_config("hyperlink", foreground="blue", underline=True)

        # 4. Crear otros componentes...
        self.create_menu()
        self.create_status_bar()

    def create_menu(self):
        # Menú simple sin CTkMenuBar
        menubar = ctk.CTkFrame(self.root, height=30)
        menubar.pack(fill="x")

        file_btn = ctk.CTkButton(menubar, text="Archivo", width=80, command=self.show_file_menu)
        file_btn.pack(side="left", padx=5)

        view_btn = ctk.CTkButton(menubar, text="Ver", width=80, command=self.show_file_menu)
        view_btn.pack(side="left", padx=5)

    def show_file_menu(self):
        menu = ctk.CTkToplevel(self.root)
        menu.geometry("200x150")

        ctk.CTkButton(menu, text="Exportar JSON", command=self.export_to_json).pack(pady=5)
        ctk.CTkButton(menu, text="Salir", command=self.root.quit).pack(pady=5)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # Título
        ctk.CTkLabel(
            self.sidebar,
            text="Configuración",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # Entrada de palabras clave
        self.keywords_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Palabras clave (separar con comas)",
            width=220
        )
        self.keywords_entry.pack(pady=5)

        # Selector de idioma
        self.language_var = ctk.StringVar(value="es")
        ctk.CTkLabel(self.sidebar, text="Idioma:").pack()
        self.language_menu = ctk.CTkOptionMenu(
            self.sidebar,
            variable=self.language_var,
            values=["es", "en", "fr", "de", "it", "pt", "ru", "zh"],
            width=220
        )
        self.language_menu.pack(pady=5)

        # Slider para máximo de artículos
        ctk.CTkLabel(self.sidebar, text="Máximo de artículos:").pack()
        self.max_articles_slider = ctk.CTkSlider(
            self.sidebar,
            from_=5,
            to=100,
            number_of_steps=19,
            width=220
        )
        self.max_articles_slider.set(20)
        self.max_articles_slider.pack(pady=5)

        # Checkbox para fuentes
        ctk.CTkLabel(self.sidebar, text="Fuentes:").pack()
        self.source_checkboxes = {}
        sources = ["NewsAPI", "GNews", "RSS Feeds", "The Guardian"]
        for source in sources:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                self.sidebar,
                text=source,
                variable=var,
                onvalue=True,
                offvalue=False
            )
            cb.pack(pady=2, anchor="w", padx=20)
            self.source_checkboxes[source] = var

        # Botón de búsqueda
        self.search_btn = ctk.CTkButton(
            self.sidebar,
            text="Buscar Noticias",
            command=self.run_scraping,
            fg_color="#2e8b57",
            hover_color="#3cb371",
            height=40,
            font=("Helvetica", 12, "bold")
        )
        self.search_btn.pack(pady=20, fill="x", padx=10)

        # Selector de idioma con callback
        self.language_var = ctk.StringVar(value="es")
        self.language_menu = ctk.CTkOptionMenu(
            self.sidebar,
            variable=self.language_var,
            values=["es", "en", "fr", "de", "it", "pt"],
            command=self.update_source_availability  # Nuevo callback
        )
        self.language_menu.pack(pady=5)

        # Panel avanzado (expandible)
        self.advanced_frame = ctk.CTkFrame(self.sidebar)
        # Panel avanzado (inicialmente oculto)
        self.advanced_label = ctk.CTkLabel(
            self.sidebar,
            text="⚙️ Opciones avanzadas (click para mostrar)",
            cursor="hand2",
            font=("Helvetica", 10)
        )
        self.advanced_label.pack(pady=(15, 0))
        self.advanced_label.bind("<Button-1>", self.toggle_advanced)

        self.advanced_frame = ctk.CTkFrame(self.sidebar, border_width=1)

        # Entrada para secciones de The Guardian
        self.guardian_section = ctk.CTkEntry(
            self.advanced_frame,
            placeholder_text="Filtrar por secciones...",
        )

        # Solo visible cuando The Guardian está seleccionado y es inglés
        self.update_advanced_visibility()

    def toggle_advanced(self, event=None):
        """Alternar la visibilidad del panel avanzado"""
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
            self.advanced_label.configure(text="⚙️ Opciones avanzadas (click para mostrar)")
        else:
            self.advanced_frame.pack(pady=(0, 10), fill="x", padx=5)
            self.advanced_label.configure(text="⚙️ Opciones avanzadas (click para ocultar)")
        self.update_advanced_visibility()

    def update_advanced_visibility(self):
        """Actualizar visibilidad de controles avanzados según selección"""
        # Ocultar todo primero
        for widget in self.advanced_frame.winfo_children():
            widget.pack_forget()

        # Mostrar controles relevantes
        lang_is_english = self.language_var.get() == "en"
        guardian_selected = self.source_checkboxes.get("The Guardian", ctk.BooleanVar(value=False)).get()

        if guardian_selected and lang_is_english:
            ctk.CTkLabel(
                self.advanced_frame,
                text="Opciones de The Guardian:",
                font=("Helvetica", 10, "bold")
            ).pack(anchor="w", pady=(5, 0))

            self.guardian_section.pack(fill="x", pady=5)

            ctk.CTkLabel(
                self.advanced_frame,
                text="Ejemplo: politics|technology|business",
                font=("Helvetica", 9)
            ).pack(anchor="w")

    def update_advanced_visibility(self):
        """Muestra/oculta controles avanzados según fuente seleccionada"""
        lang_is_english = self.language_var.get() == "en"
        guardian_selected = self.source_checkboxes["The Guardian"].get()

        if guardian_selected and lang_is_english:
            self.guardian_section.pack(pady=5)
        else:
            self.guardian_section.pack_forget()

    def create_results_area(self):
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Pestañas
        self.tabview = ctk.CTkTabview(self.results_frame)
        self.tabview.pack(fill="both", expand=True)

        self.tab_list = self.tabview.add("Lista")
        self.tab_grid = self.tabview.add("Cuadrícula")
        self.tab_sources = self.tabview.add("Por Fuente")

        # Lista de artículos
        self.article_list = ctk.CTkScrollableFrame(self.tab_list)
        self.article_list.pack(fill="both", expand=True)

        # Cuadrícula (placeholder)
        self.grid_frame = ctk.CTkScrollableFrame(self.tab_grid)
        self.grid_frame.pack(fill="both", expand=True)

        # Por fuente (placeholder)
        self.sources_frame = ctk.CTkScrollableFrame(self.tab_sources)
        self.sources_frame.pack(fill="both", expand=True)

    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(fill="x", padx=10, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Listo",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=10)

        self.progress = ctk.CTkProgressBar(
            self.status_bar,
            mode="indeterminate",
            width=200,
            height=15
        )
        self.progress.pack(side="right", padx=10)
        self.progress.set(0)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def update_status(self, message):
        self.status_label.configure(text=message)
        self.root.update()

    def run_scraping(self):
        # Obtener parámetros básicos
        keywords = [k.strip() for k in self.keywords_entry.get().split(",") if k.strip()]
        if not keywords:
            messagebox.showwarning("Advertencia", "Debe ingresar al menos una palabra clave")
            return

        language = self.language_var.get()
        max_articles = int(self.max_articles_slider.get())

        # Determinar fuentes activas
        active_sources = []
        if self.source_checkboxes["NewsAPI"].get():
            active_sources.append("newsapi")
        if self.source_checkboxes["GNews"].get():
            active_sources.append("gnews")
        if self.source_checkboxes["RSS Feeds"].get():
            active_sources.append("rss")
        if self.source_checkboxes["The Guardian"].get() and language == "en":
            active_sources.append("theguardian")

        # Preparar parámetros específicos
        scraper_params = {}
        if "theguardian" in active_sources:
            if hasattr(self, 'guardian_section') and self.guardian_section.get():
                scraper_params["theguardian_section"] = self.guardian_section.get()

        # Configurar UI para búsqueda
        self.search_btn.configure(state="disabled")
        self.progress.start()
        self.update_status("Buscando artículos...")

        # Iniciar el hilo de scraping
        threading.Thread(
            target=self._async_scraping_wrapper,
            args=(keywords, language, max_articles, active_sources),
            kwargs=scraper_params,
            daemon=True
        ).start()

    def _async_scraping_wrapper(self, keywords, language, max_articles, active_sources=None, **kwargs):
        """
        Wrapper para ejecutar asyncio desde un hilo

        Args:
            keywords: Lista de palabras clave
            language: Código de idioma
            max_articles: Máximo de artículos por fuente
            active_sources: Lista de fuentes activas (opcional)
            **kwargs: Parámetros adicionales para scrapers específicos
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            articles = loop.run_until_complete(
                scrape_all_sources(
                    keywords=keywords,
                    language=language,
                    max_articles=max_articles,
                    active_sources=active_sources,
                    **kwargs
                )
            )
            self.root.after(0, self.display_results, articles, kwargs)  # Pasar kwargs para feedback

        except ValueError as ve:
            self.root.after(0, messagebox.showwarning, "Validación fallida", str(ve))
        except aiohttp.ClientError as ce:
            self.root.after(0, messagebox.showerror, "Error de conexión",
                            f"No se pudo conectar al servicio:\n{str(ce)}")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error inesperado",
                            f"Ocurrió un error:\n{str(e)}")
        finally:
            self.root.after(0, self._reset_ui)
            loop.close()

    def display_results(self, articles, scraper_params=None):
        """Muestra los resultados de búsqueda con formato mejorado

        Args:
            articles: Lista de artículos encontrados
            scraper_params: Parámetros usados en la búsqueda (opcional)
        """
        if scraper_params is None:
            scraper_params = {}

        # Limpiar el área de resultados
        self.results_text.delete("1.0", "end")

        # Configurar tags para formato especial
        ##self.results_text.tag_config("header", font=("Helvetica", 12, "bold"))
        ##self.results_text.tag_config("param", font=("Helvetica", 10, "italic"))
        self.results_text.tag_config("warning", foreground="orange")

        # Mostrar resumen de búsqueda
        # Aplicar formato usando marcas en lugar de fuentes directas
        self.results_text.insert("end", "⚙️ Parámetros de Búsqueda\n")
        self.results_text.tag_add("header", "1.0", "2.0")
        self.results_text.insert("end",
                                 f"🔎 Palabras clave: {', '.join(scraper_params.get('keywords', [])) or 'Todas'}\n")
        self.results_text.insert("end", f"🌐 Idioma: {scraper_params.get('language', 'No especificado')}\n")
        self.results_text.insert("end", f"📊 Máx. artículos: {scraper_params.get('max_articles', 'No especificado')}\n")

        # Mostrar parámetros específicos por fuente
        if "theguardian_section" in scraper_params:
            self.results_text.insert("end",
                                     f"📰 The Guardian - Secciones: {scraper_params['theguardian_section']}\n",
                                     "param")

        self.results_text.insert("end", "\n🔍 Resultados Obtenidos\n\n", "header")

        if not articles:
            self.results_text.insert("end",
                                     "⚠️ No se encontraron artículos con los criterios especificados\n",
                                     "warning")
            return

        self.results_text.insert("end", f"✅ Encontrados: {len(articles)} artículos\n\n")

        # Mostrar cada artículo con formato
        for i, article in enumerate(articles, 1):
            self.results_text.insert("end", f"📌 Artículo #{i}\n", "header")
            self.results_text.insert("end", f"📰 Título: {article.get('title', 'Sin título')}\n")

            if article.get('source'):
                self.results_text.insert("end", f"🏢 Fuente: {article['source']}\n")

            if article.get('published_at'):
                self.results_text.insert("end", f"📅 Fecha: {article['published_at']}\n")

            if article.get('author'):
                self.results_text.insert("end", f"✍️ Autor: {article['author']}\n")

            if article.get('description'):
                self.results_text.insert("end", "\nℹ️ Descripción:\n")
                self.results_text.insert("end", f"{article['description']}\n")

            if article.get('url'):
                self.results_text.insert("end", "\n🔗 Enlace: ")
                self.results_text.insert("end", f"{article['url']}\n", "hyperlink")
                self.results_text.tag_bind("hyperlink", "<Button-1>",
                                           lambda e, url=article['url']: webbrowser.open(url))

            self.results_text.insert("end", "\n" + "─" * 50 + "\n\n")

        # Añadir funcionalidad de hipervínculos
        self.results_text.tag_config("hyperlink", foreground="blue", underline=True)
        self.results_text.tag_bind("hyperlink", "<Enter>",
                                   lambda e: self.results_text.config(cursor="hand2"))
        self.results_text.tag_bind("hyperlink", "<Leave>",
                                   lambda e: self.results_text.config(cursor=""))

        # Auto-ajustar el scroll al inicio
        self.results_text.see("1.0")

    def _create_article_card(self, index, article):
        card = ctk.CTkFrame(
            self.article_list,
            border_width=1,
            border_color="#3a3a3a",
            corner_radius=8
        )
        card.pack(fill="x", pady=5, padx=5)

        # Encabezado
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(5, 0))

        ctk.CTkLabel(
            header,
            text=f"Artículo #{index}",
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"Fuente: {article.get('source', 'Desconocida')}",
            font=("Helvetica", 10),
            anchor="e"
        ).pack(side="right")

        # Título
        title = ctk.CTkLabel(
            card,
            text=article.get('title', 'Sin título'),
            font=("Helvetica", 14, "bold"),
            wraplength=700,
            justify="left",
            anchor="w"
        )
        title.pack(fill="x", padx=10, pady=(0, 5))

        # Descripción
        if article.get('description'):
            desc = ctk.CTkLabel(
                card,
                text=article['description'],
                font=("Helvetica", 12),
                wraplength=700,
                justify="left"
            )
            desc.pack(fill="x", padx=10, pady=5)

        # Pie de tarjeta
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=5, pady=(0, 5))

        if article.get('published_at'):
            ctk.CTkLabel(
                footer,
                text=f"Publicado: {article['published_at']}",
                font=("Helvetica", 10)
            ).pack(side="left")

        if article.get('url'):
            btn = ctk.CTkButton(
                footer,
                text="Abrir en navegador",
                command=lambda url=article['url']: webbrowser.open(url),
                width=120,
                height=25,
                font=("Helvetica", 10)
            )
            btn.pack(side="right")

    def export_to_json(self):
        if not self.articles:
            messagebox.showwarning("Advertencia", "No hay artículos para exportar")
            return

        filename = f"noticias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Éxito", f"Artículos exportados a {filename}")

    def export_to_csv(self):
        # Implementación similar a export_to_json
        pass

    def update_source_availability(self, *args):
        """Habilita/deshabilita fuentes según el idioma seleccionado"""
        current_lang = self.language_var.get()

        # Buscar el checkbox de The Guardian
        for name, var in self.source_checkboxes.items():
            if "guardian" in name.lower():
                checkbox = None
                # Encontrar el widget checkbox real (puede necesitar ajustes según tu implementación)
                for widget in self.sidebar.winfo_children():
                    if hasattr(widget, '_text') and widget._text == name:
                        checkbox = widget
                        break

                if checkbox:
                    if current_lang != "en":
                        checkbox.configure(state="disabled")
                        var.set(False)
                    else:
                        checkbox.configure(state="normal")

        self.update_advanced_visibility()

    def _reset_ui(self):
        self.progress.stop()
        self.progress.set(0)
        self.search_btn.configure(state="normal")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = NewsScraperApp()
    app.run()