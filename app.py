"""
OFX to CSV Consolidator
GUI Application for processing multiple OFX files and exporting to CSV/Excel
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from datetime import datetime
from ofx_processor import OFXProcessor


class OFXConsolidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OFX Consolidador - Extratos Bancários")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        self.processor = OFXProcessor()
        self.selected_files = []
        self.df_result = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="📊 Consolidador de Extratos OFX",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=10)

        # File selection section
        self.setup_file_selection(main_frame)

        # File list section
        self.setup_file_list(main_frame)

        # Options section
        self.setup_options(main_frame)

        # Process button
        self.setup_process_button(main_frame)

        # Results section
        self.setup_results(main_frame)

        # Status bar
        self.setup_status_bar(main_frame)

    def setup_file_selection(self, parent):
        """Setup file selection section"""
        file_frame = ttk.LabelFrame(parent, text="Arquivos OFX", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(
            file_frame,
            text="📁 Adicionar Arquivos OFX",
            command=self.add_files
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            file_frame,
            text="🗑️ Limpar Lista",
            command=self.clear_files
        ).grid(row=0, column=1, padx=5, sticky=tk.W)

        self.file_count_label = ttk.Label(file_frame, text="Nenhum arquivo selecionado")
        self.file_count_label.grid(row=0, column=2, padx=5, sticky=tk.E)

    def setup_file_list(self, parent):
        """Setup file list display"""
        list_frame = ttk.LabelFrame(parent, text="Arquivos Selecionados", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Create Treeview
        columns = ('arquivo', 'tamanho', 'caminho')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.file_tree.heading('arquivo', text='Arquivo')
        self.file_tree.heading('tamanho', text='Tamanho')
        self.file_tree.heading('caminho', text='Caminho Completo')

        self.file_tree.column('arquivo', width=200)
        self.file_tree.column('tamanho', width=100)
        self.file_tree.column('caminho', width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscroll=scrollbar.set)

        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def setup_options(self, parent):
        """Setup processing options"""
        options_frame = ttk.LabelFrame(parent, text="Opções", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # Remove duplicates option
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Remover transações duplicadas (baseado no ID da transação)",
            variable=self.remove_duplicates_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        # Include time option
        self.include_time_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Incluir coluna de horário (hh:mm:ss)",
            variable=self.include_time_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        # Export format
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=2, column=0, sticky=tk.W, pady=5)

        ttk.Label(format_frame, text="Formato de exportação:").pack(side=tk.LEFT, padx=5)

        self.export_format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(
            format_frame,
            text="CSV (separado por ;)",
            variable=self.export_format_var,
            value="csv"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.export_format_var,
            value="excel"
        ).pack(side=tk.LEFT, padx=5)

    def setup_process_button(self, parent):
        """Setup process button"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, pady=10)

        self.process_button = ttk.Button(
            button_frame,
            text="⚡ Processar e Exportar",
            command=self.process_files,
            style='Accent.TButton'
        )
        self.process_button.pack()

    def setup_results(self, parent):
        """Setup results display"""
        results_frame = ttk.LabelFrame(parent, text="Resultados", padding="10")
        results_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(
            parent,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def add_files(self):
        """Add OFX files to the list"""
        files = filedialog.askopenfilenames(
            title="Selecione os arquivos OFX",
            filetypes=[("OFX Files", "*.ofx"), ("All Files", "*.*")]
        )

        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)

                    # Get file size
                    size = os.path.getsize(file_path)
                    size_str = self.format_size(size)

                    # Add to treeview
                    self.file_tree.insert(
                        '',
                        tk.END,
                        values=(os.path.basename(file_path), size_str, file_path)
                    )

            self.update_file_count()

    def clear_files(self):
        """Clear all selected files"""
        self.selected_files = []
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.update_file_count()
        self.results_text.delete(1.0, tk.END)

    def update_file_count(self):
        """Update file count label"""
        count = len(self.selected_files)
        if count == 0:
            self.file_count_label.config(text="Nenhum arquivo selecionado")
        elif count == 1:
            self.file_count_label.config(text="1 arquivo selecionado")
        else:
            self.file_count_label.config(text=f"{count} arquivos selecionados")

    def format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def process_files(self):
        """Process selected OFX files"""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return

        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Processando arquivos...")
        self.process_button.config(state='disabled')
        self.root.update()

        try:
            # Process files
            self.log_message("Iniciando processamento...\n")

            self.df_result = self.processor.process_multiple_files(
                self.selected_files,
                remove_duplicates=self.remove_duplicates_var.get()
            )

            if self.df_result.empty:
                self.log_message("ERRO: Nenhuma transação encontrada nos arquivos!\n")
                messagebox.showerror("Erro", "Nenhuma transação foi encontrada nos arquivos OFX.")
                return

            # Show processing summary
            self.show_summary()

            # Ask for save location
            self.save_results()

        except Exception as e:
            self.log_message(f"ERRO: {str(e)}\n")
            messagebox.showerror("Erro", f"Erro ao processar arquivos:\n{str(e)}")

        finally:
            self.process_button.config(state='normal')
            self.status_var.set("Pronto")

    def show_summary(self):
        """Show processing summary"""
        summary = self.processor.get_summary(self.df_result)

        self.log_message("=" * 60 + "\n")
        self.log_message("RESUMO DO PROCESSAMENTO\n")
        self.log_message("=" * 60 + "\n\n")

        self.log_message(f"Total de transações: {summary['total_transacoes']}\n")
        self.log_message(f"  - Créditos: {summary['total_creditos']} (R$ {summary['soma_creditos']:,.2f})\n")
        self.log_message(f"  - Débitos: {summary['total_debitos']} (R$ {summary['soma_debitos']:,.2f})\n")
        self.log_message(f"  - Saldo líquido: R$ {summary['saldo_liquido']:,.2f}\n\n")

        self.log_message(f"Bancos distintos: {summary['bancos']}\n")
        self.log_message(f"Contas distintas: {summary['contas']}\n")
        self.log_message(f"Arquivos processados: {summary['arquivos_processados']}\n")

        if summary['arquivos_com_erro'] > 0:
            self.log_message(f"Arquivos com erro: {summary['arquivos_com_erro']}\n")

        # Show errors if any
        if self.processor.errors:
            self.log_message("\nERROS ENCONTRADOS:\n")
            for error in self.processor.errors:
                self.log_message(f"  - {error}\n")

        self.log_message("\n" + "=" * 60 + "\n\n")

    def save_results(self):
        """Save results to file"""
        export_format = self.export_format_var.get()

        if export_format == "csv":
            default_ext = ".csv"
            filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")]
        else:
            default_ext = ".xlsx"
            filetypes = [("Excel Files", "*.xlsx"), ("All Files", "*.*")]

        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"extratos_consolidados_{timestamp}{default_ext}"

        save_path = filedialog.asksaveasfilename(
            title="Salvar arquivo consolidado",
            defaultextension=default_ext,
            initialfile=default_filename,
            filetypes=filetypes
        )

        if save_path:
            try:
                include_time = self.include_time_var.get()

                if export_format == "csv":
                    success = self.processor.export_to_csv(
                        self.df_result,
                        save_path,
                        include_time=include_time
                    )
                else:
                    success = self.processor.export_to_excel(
                        self.df_result,
                        save_path,
                        include_time=include_time
                    )

                if success:
                    self.log_message(f"Arquivo salvo com sucesso em:\n{save_path}\n")
                    messagebox.showinfo(
                        "Sucesso",
                        f"Arquivo exportado com sucesso!\n\n{save_path}"
                    )
                else:
                    messagebox.showerror("Erro", "Falha ao exportar arquivo.")

            except Exception as e:
                self.log_message(f"Erro ao salvar arquivo: {str(e)}\n")
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")

    def log_message(self, message):
        """Log message to results text area"""
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
        self.root.update()


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    style.theme_use('clam')

    # Create and run app
    app = OFXConsolidatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
