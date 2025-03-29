"""
GUI module for 8086 simulator.
Implements a emu8086-like graphical user interface.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
from tkinter.constants import *

try:
    from pygments import highlight
    from pygments.lexers import NasmLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class SimulatorGUI:
    """Graphical user interface for the 8086 simulator."""
    
    def __init__(self, cpu, memory, assembler, debugger):
        """Initialize the GUI with simulator components."""
        self.cpu = cpu
        self.memory = memory
        self.assembler = assembler
        self.debugger = debugger
        self.current_file = None
        self.is_running = False
        self.step_mode = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("8086 Microprocessor Simulator")
        self.root.geometry("1200x800")
        
        # Create a custom font for monospace text
        self.mono_font = font.Font(family="Courier", size=10)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.create_layout()
        
        # Set up key bindings
        self.setup_bindings()
        
        # Update the UI
        self.update_display()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.code_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.code_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.code_editor.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Assemble", command=self.assemble_code, accelerator="F9")
        run_menu.add_command(label="Run", command=self.run_program, accelerator="F5")
        run_menu.add_command(label="Step", command=self.step_instruction, accelerator="F7")
        run_menu.add_command(label="Reset", command=self.reset_simulator, accelerator="F2")
        menubar.add_cascade(label="Run", menu=run_menu)
        
        # Debug menu
        debug_menu = tk.Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Toggle Breakpoint", command=self.toggle_breakpoint, accelerator="F8")
        debug_menu.add_command(label="Clear All Breakpoints", command=self.clear_breakpoints)
        menubar.add_cascade(label="Debug", menu=debug_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Memory", command=self.show_memory_window)
        view_menu.add_command(label="I/O Ports", command=self.show_io_ports_window)
        view_menu.add_command(label="Stack", command=self.show_stack_window)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_layout(self):
        """Create the main application layout."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create a toolbar
        self.create_toolbar(main_frame)
        
        # Split the window into left (code) and right (registers/etc) panels
        paned_window = ttk.PanedWindow(main_frame, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=True, pady=5)
        
        # Left panel - Code editor
        code_frame = ttk.LabelFrame(paned_window, text="Assembly Code")
        
        # Code editor with line numbers
        editor_frame = ttk.Frame(code_frame)
        editor_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, pady=5, takefocus=0,
                               bg='lightgrey', border=0, font=self.mono_font)
        self.line_numbers.pack(side=LEFT, fill=Y)
        
        # Main code editor
        self.code_editor = scrolledtext.ScrolledText(editor_frame, wrap=NONE, font=self.mono_font)
        self.code_editor.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Add sample code
        self.code_editor.insert(END, "; Sample 8086 Assembly Program\n\n"
                                     "        .MODEL SMALL\n"
                                     "        .STACK 100h\n\n"
                                     "        .DATA\n"
                                     "message DB 'Hello, World!$'\n\n"
                                     "        .CODE\n"
                                     "main    PROC\n"
                                     "        ; Initialize data segment\n"
                                     "        MOV AX, @DATA\n"
                                     "        MOV DS, AX\n\n"
                                     "        ; Display the message\n"
                                     "        MOV AH, 09h      ; DOS function: output string\n"
                                     "        MOV DX, OFFSET message\n"
                                     "        INT 21h          ; Call DOS\n\n"
                                     "        ; Exit program\n"
                                     "        MOV AX, 4C00h    ; DOS function: terminate with return code\n"
                                     "        INT 21h          ; Call DOS\n"
                                     "main    ENDP\n"
                                     "        END main\n")
        
        # Configure line numbers
        self.update_line_numbers()
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)
        
        # Add to paned window
        paned_window.add(code_frame, weight=3)
        
        # Right panel - Registers, Flags, and Memory
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=1)
        
        # Registers panel
        reg_frame = ttk.LabelFrame(right_panel, text="Registers")
        reg_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create register display
        self.reg_displays = {}
        for row, regs in enumerate([
            ("AX", "BX"),
            ("CX", "DX"),
            ("SP", "BP"),
            ("SI", "DI"),
            ("CS", "DS"),
            ("SS", "ES"),
            ("IP", "FLAGS")
        ]):
            for col, reg in enumerate(regs):
                ttk.Label(reg_frame, text=f"{reg}:").grid(row=row, column=col*2, padx=5, pady=2, sticky=W)
                var = tk.StringVar(value="0000")
                entry = ttk.Entry(reg_frame, textvariable=var, width=6, font=self.mono_font)
                entry.grid(row=row, column=col*2+1, padx=5, pady=2, sticky=W)
                self.reg_displays[reg] = var
        
        # Flags panel
        flags_frame = ttk.LabelFrame(right_panel, text="Flags")
        flags_frame.pack(fill=X, padx=5, pady=5)
        
        # Create flag display
        self.flag_displays = {}
        flags_grid = ttk.Frame(flags_frame)
        flags_grid.pack(fill=X, padx=5, pady=5)
        
        flags = ["CF", "PF", "AF", "ZF", "SF", "TF", "IF", "DF", "OF"]
        for col, flag in enumerate(flags):
            ttk.Label(flags_grid, text=flag).grid(row=0, column=col, padx=2)
            var = tk.StringVar(value="0")
            chk = ttk.Checkbutton(flags_grid, variable=var, state="disabled")
            chk.grid(row=1, column=col, padx=2)
            self.flag_displays[flag] = var
        
        # Memory viewer panel (shows a small preview, full view in separate window)
        mem_frame = ttk.LabelFrame(right_panel, text="Memory Preview")
        mem_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create memory display (simple preview)
        self.memory_display = scrolledtext.ScrolledText(mem_frame, height=10, width=40, 
                                                  wrap=NONE, font=self.mono_font)
        self.memory_display.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.memory_display.config(state=DISABLED)
        
        # Create bottom status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=X, side=BOTTOM, pady=2)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=W)
        status_label.pack(side=LEFT, fill=X, padx=5)
        
        # Create output console
        console_frame = ttk.LabelFrame(main_frame, text="Console Output")
        console_frame.pack(fill=X, expand=False, side=BOTTOM, padx=5, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=6, wrap=WORD, font=self.mono_font)
        self.console.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.console.config(state=DISABLED)
    
    def create_toolbar(self, parent):
        """Create the application toolbar."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=X, padx=5, pady=2)
        
        # New file button
        new_btn = ttk.Button(toolbar, text="New", command=self.new_file)
        new_btn.pack(side=LEFT, padx=2)
        
        # Open file button
        open_btn = ttk.Button(toolbar, text="Open", command=self.open_file)
        open_btn.pack(side=LEFT, padx=2)
        
        # Save file button
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side=LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Assemble button
        assemble_btn = ttk.Button(toolbar, text="Assemble", command=self.assemble_code)
        assemble_btn.pack(side=LEFT, padx=2)
        
        # Run button
        run_btn = ttk.Button(toolbar, text="Run", command=self.run_program)
        run_btn.pack(side=LEFT, padx=2)
        
        # Step button
        step_btn = ttk.Button(toolbar, text="Step", command=self.step_instruction)
        step_btn.pack(side=LEFT, padx=2)
        
        # Reset button
        reset_btn = ttk.Button(toolbar, text="Reset", command=self.reset_simulator)
        reset_btn.pack(side=LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Breakpoint button
        bp_btn = ttk.Button(toolbar, text="Toggle Breakpoint", command=self.toggle_breakpoint)
        bp_btn.pack(side=LEFT, padx=2)
    
    def setup_bindings(self):
        """Set up keyboard shortcuts."""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F9>', lambda e: self.assemble_code())
        self.root.bind('<F5>', lambda e: self.run_program())
        self.root.bind('<F7>', lambda e: self.step_instruction())
        self.root.bind('<F2>', lambda e: self.reset_simulator())
        self.root.bind('<F8>', lambda e: self.toggle_breakpoint())
    
    def update_line_numbers(self, event=None):
        """Update the line numbers in the editor."""
        self.line_numbers.config(state=NORMAL)
        self.line_numbers.delete(1.0, END)
        
        count = self.code_editor.get(1.0, END).count('\n')
        for i in range(1, count + 1):
            self.line_numbers.insert(END, f"{i}\n")
        
        self.line_numbers.config(state=DISABLED)
        
        # Sync scroll position
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])
    
    def log_message(self, message):
        """Add a message to the console output."""
        self.console.config(state=NORMAL)
        self.console.insert(END, message + "\n")
        self.console.see(END)
        self.console.config(state=DISABLED)
    
    def update_display(self):
        """Update all display elements with current simulator state."""
        # Update registers
        reg_state = self.cpu.get_register_state()
        for reg, display in self.reg_displays.items():
            display.set(f"{reg_state.get(reg, 0):04X}")
        
        # Update flags
        flag_state = self.cpu.get_flag_state()
        for flag, display in self.flag_displays.items():
            display.set("1" if flag_state.get(flag, 0) else "0")
        
        # Update memory preview
        self.memory_display.config(state=NORMAL)
        self.memory_display.delete(1.0, END)
        
        # Display memory at CS:IP
        cs = self.cpu.get_register(self.cpu.CS)
        ip = self.cpu.get_register(self.cpu.IP)
        start_address = self.cpu.get_physical_address(cs, ip)
        length = 96  # Show 6 rows of 16 bytes
        
        # Format memory similar to a hex editor
        self.memory_display.insert(END, "Address    | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII\n")
        self.memory_display.insert(END, "-----------+-------------------------------------------------+----------------\n")
        
        for row in range(0, length, 16):
            addr = start_address + row
            line = f"{addr:08X} | "
            ascii_chars = ""
            
            for col in range(16):
                if row + col < length:
                    try:
                        value = self.memory.read_byte(addr + col)
                        line += f"{value:02X} "
                        
                        # Add to ASCII representation
                        if 32 <= value <= 126:  # Printable ASCII
                            ascii_chars += chr(value)
                        else:
                            ascii_chars += "."
                    except Exception:
                        line += "-- "
                        ascii_chars += " "
                else:
                    line += "   "
                    ascii_chars += " "
            
            line += f"| {ascii_chars}\n"
            self.memory_display.insert(END, line)
        
        self.memory_display.config(state=DISABLED)
    
    # File operations
    def new_file(self):
        """Create a new file."""
        if self.current_file and not self.save_if_modified():
            return
        
        self.code_editor.delete(1.0, END)
        self.current_file = None
        self.status_var.set("New file created")
    
    def open_file(self):
        """Open a file."""
        if self.current_file and not self.save_if_modified():
            return
        
        filepath = filedialog.askopenfilename(
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            self.code_editor.delete(1.0, END)
            self.code_editor.insert(END, content)
            self.current_file = filepath
            self.status_var.set(f"Opened: {filepath}")
            self.update_line_numbers()
            
            # Reset the simulator when a new file is loaded
            self.reset_simulator()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            content = self.code_editor.get(1.0, END)
            with open(self.current_file, 'w') as f:
                f.write(content)
            self.status_var.set(f"Saved: {self.current_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            return False
    
    def save_file_as(self):
        """Save the current file with a new name."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".asm",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return False
        
        self.current_file = filepath
        return self.save_file()
    
    def save_if_modified(self):
        """Check if the current file is modified and offer to save it."""
        # In a real implementation, you'd track modifications
        if messagebox.askyesno("Save Changes", 
                               "The current file has been modified. Save changes?"):
            return self.save_file()
        return True
    
    def select_all(self):
        """Select all text in the editor."""
        self.code_editor.tag_add(SEL, "1.0", END)
        self.code_editor.mark_set(INSERT, "1.0")
        self.code_editor.see(INSERT)
        return 'break'
    
    # Simulator operations
    def assemble_code(self):
        """Assemble the current code."""
        if not self.save_if_modified():
            return
        
        try:
            # Reset the CPU and memory
            self.cpu.reset()
            self.memory.reset()
            
            # Create a temporary file if needed
            if not self.current_file:
                temp_file = os.path.join(os.getcwd(), "temp.asm")
                with open(temp_file, 'w') as f:
                    f.write(self.code_editor.get(1.0, END))
                self.assembler.load_program(temp_file)
                os.remove(temp_file)  # Clean up
            else:
                self.assembler.load_program(self.current_file)
            
            self.log_message("Program assembled successfully")
            self.status_var.set("Program assembled")
            self.update_display()
        except Exception as e:
            self.log_message(f"Assembly error: {str(e)}")
            messagebox.showerror("Assembly Error", str(e))
    
    def run_program(self):
        """Run the program until completion or breakpoint."""
        if self.cpu.halted:
            self.log_message("CPU is halted. Reset to continue.")
            return
        
        self.log_message("Running program...")
        self.is_running = True
        
        # Run in a way that lets the UI remain responsive
        # In a real implementation, this would be more sophisticated
        # with proper thread management or scheduling
        self.root.after(10, self.continue_execution)
    
    def continue_execution(self):
        """Continue program execution (used by run_program)."""
        if not self.is_running:
            return
        
        # Run for a small batch of instructions
        executed = 0
        batch_size = 100  # Adjust based on desired responsiveness
        
        while executed < batch_size and self.is_running and not self.cpu.halted:
            # Check for breakpoint
            cs = self.cpu.get_register(self.cpu.CS)
            ip = self.cpu.get_register(self.cpu.IP)
            physical_address = self.cpu.get_physical_address(cs, ip)
            
            if physical_address in self.debugger.breakpoints:
                self.log_message(f"Breakpoint hit at {cs:04X}:{ip:04X}")
                self.is_running = False
                break
            
            # Execute one instruction
            result = self.cpu.execute_instruction()
            if not result:
                self.is_running = False
                break
            
            executed += 1
        
        # Update the display
        self.update_display()
        
        # Continue if still running
        if self.is_running:
            self.root.after(10, self.continue_execution)
        else:
            if self.cpu.halted:
                self.log_message("Program execution completed (CPU halted)")
            else:
                self.log_message("Program execution paused")
    
    def step_instruction(self):
        """Execute a single instruction."""
        if self.cpu.halted:
            self.log_message("CPU is halted. Reset to continue.")
            return
        
        result = self.debugger.step_instruction()
        
        if result:
            cs = self.cpu.get_register(self.cpu.CS)
            ip = self.cpu.get_register(self.cpu.IP)
            self.log_message(f"Stepped to {cs:04X}:{ip:04X}")
        else:
            if self.cpu.halted:
                self.log_message("CPU halted")
            else:
                self.log_message("Step failed")
        
        self.update_display()
    
    def reset_simulator(self):
        """Reset the simulator to initial state."""
        self.cpu.reset()
        self.memory.reset()
        self.is_running = False
        self.log_message("Simulator reset")
        self.status_var.set("Simulator reset")
        self.update_display()
    
    def toggle_breakpoint(self):
        """Toggle a breakpoint at the current instruction pointer or selected line."""
        try:
            # Get cursor position in the code
            cursor_pos = self.code_editor.index(INSERT)
            line_num = int(cursor_pos.split('.')[0])
            
            # This is simplified - in a real implementation you would need to:
            # 1. Map the editor line to the actual instruction address
            # 2. Toggle the breakpoint at that address
            
            # For now, just toggle at current IP
            cs = self.cpu.get_register(self.cpu.CS)
            ip = self.cpu.get_register(self.cpu.IP)
            addr = self.cpu.get_physical_address(cs, ip)
            
            if self.debugger.toggle_breakpoint(addr):
                self.log_message(f"Breakpoint set at {cs:04X}:{ip:04X}")
            else:
                self.log_message(f"Breakpoint removed from {cs:04X}:{ip:04X}")
            
            # In a real implementation, you'd highlight the breakpoint in the editor
        except Exception as e:
            self.log_message(f"Error setting breakpoint: {str(e)}")
    
    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.debugger.clear_breakpoints()
        self.log_message("All breakpoints cleared")
    
    # Additional views
    def show_memory_window(self):
        """Show a detailed memory view window."""
        memory_window = tk.Toplevel(self.root)
        memory_window.title("Memory Viewer")
        memory_window.geometry("800x600")
        
        # Create a full-featured memory viewer
        frame = ttk.Frame(memory_window, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        # Address entry
        addr_frame = ttk.Frame(frame)
        addr_frame.pack(fill=X, pady=5)
        
        ttk.Label(addr_frame, text="Start Address (hex):").pack(side=LEFT, padx=5)
        addr_var = tk.StringVar(value="00000")
        addr_entry = ttk.Entry(addr_frame, textvariable=addr_var, width=10)
        addr_entry.pack(side=LEFT, padx=5)
        
        ttk.Label(addr_frame, text="Length:").pack(side=LEFT, padx=5)
        length_var = tk.StringVar(value="256")
        length_entry = ttk.Entry(addr_frame, textvariable=length_var, width=10)
        length_entry.pack(side=LEFT, padx=5)
        
        # Memory display
        mem_display = scrolledtext.ScrolledText(frame, font=self.mono_font, wrap=NONE)
        mem_display.pack(fill=BOTH, expand=True, pady=5)
        
        # Function to update memory display
        def update_memory():
            try:
                start = int(addr_var.get(), 16)
                length = int(length_var.get())
                
                mem_display.config(state=NORMAL)
                mem_display.delete(1.0, END)
                
                # Header
                mem_display.insert(END, "Address    | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII\n")
                mem_display.insert(END, "-----------+-------------------------------------------------+----------------\n")
                
                for row in range(0, length, 16):
                    addr = start + row
                    line = f"{addr:08X} | "
                    ascii_chars = ""
                    
                    for col in range(16):
                        if row + col < length:
                            try:
                                value = self.memory.read_byte(addr + col)
                                line += f"{value:02X} "
                                
                                # Add to ASCII representation
                                if 32 <= value <= 126:  # Printable ASCII
                                    ascii_chars += chr(value)
                                else:
                                    ascii_chars += "."
                            except Exception:
                                line += "-- "
                                ascii_chars += " "
                        else:
                            line += "   "
                            ascii_chars += " "
                    
                    line += f"| {ascii_chars}\n"
                    mem_display.insert(END, line)
                
                mem_display.config(state=DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Error displaying memory: {str(e)}")
        
        # Update button
        update_btn = ttk.Button(addr_frame, text="Update", command=update_memory)
        update_btn.pack(side=LEFT, padx=20)
        
        # Initial update
        update_memory()
    
    def show_io_ports_window(self):
        """Show I/O ports view window."""
        ports_window = tk.Toplevel(self.root)
        ports_window.title("I/O Ports")
        ports_window.geometry("600x400")
        
        # Create an I/O ports viewer (simplified)
        frame = ttk.Frame(ports_window, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(frame, text="I/O Ports View").pack(pady=10)
        ttk.Label(frame, text="This feature is not yet implemented").pack(pady=20)
    
    def show_stack_window(self):
        """Show stack view window."""
        stack_window = tk.Toplevel(self.root)
        stack_window.title("Stack Viewer")
        stack_window.geometry("400x600")
        
        # Create a stack viewer
        frame = ttk.Frame(stack_window, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(frame, text="Stack View").pack(pady=5)
        
        # Stack display
        stack_display = scrolledtext.ScrolledText(frame, font=self.mono_font, height=20)
        stack_display.pack(fill=BOTH, expand=True, pady=5)
        
        # Function to update stack display
        def update_stack():
            try:
                stack_display.config(state=NORMAL)
                stack_display.delete(1.0, END)
                
                # Get stack segment and pointer
                ss = self.cpu.get_register(self.cpu.SS)
                sp = self.cpu.get_register(self.cpu.SP)
                bp = self.cpu.get_register(self.cpu.BP)
                
                # Show some values above and below SP
                stack_top = self.cpu.get_physical_address(ss, 0xFFFE)
                current_sp = self.cpu.get_physical_address(ss, sp)
                current_bp = self.cpu.get_physical_address(ss, bp)
                
                # Display header
                stack_display.insert(END, "Address    | Value  | Notes\n")
                stack_display.insert(END, "-----------+--------+------------------\n")
                
                # Display stack values (from top to bottom)
                for offset in range(0, 32, 2):
                    addr = current_sp + offset
                    if addr <= stack_top:
                        try:
                            value = self.memory.read_word(addr)
                            
                            notes = ""
                            if addr == current_sp:
                                notes = "<-- SP"
                            elif addr == current_bp:
                                notes = "<-- BP"
                            
                            line = f"{addr:08X} | {value:04X}   | {notes}\n"
                            stack_display.insert(END, line)
                        except Exception:
                            break
                
                stack_display.config(state=DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Error displaying stack: {str(e)}")
        
        # Update button
        update_btn = ttk.Button(frame, text="Refresh", command=update_stack)
        update_btn.pack(pady=10)
        
        # Initial update
        update_stack()
    
    # Help and about dialogs
    def show_documentation(self):
        """Show documentation."""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("8086 Simulator Documentation")
        doc_window.geometry("800x600")
        
        frame = ttk.Frame(doc_window, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        docs = scrolledtext.ScrolledText(frame, wrap=WORD)
        docs.pack(fill=BOTH, expand=True)
        
        documentation = """
        # 8086 Microprocessor Simulator
        
        This simulator provides a comprehensive environment for writing, assembling, and debugging 8086 assembly code.
        
        ## Features
        
        - Complete 8086 instruction set implementation
        - Register visualization and manipulation
        - Memory viewing and editing
        - Step-by-step execution mode
        - Breakpoint functionality
        - Flag status display
        - Basic I/O operations support
        
        ## Basic Usage
        
        1. Write or load an assembly program in the code editor
        2. Assemble the code (F9)
        3. Run the program (F5) or step through it (F7)
        4. Reset the simulator (F2) to start over
        
        ## Keyboard Shortcuts
        
        - Ctrl+N: New file
        - Ctrl+O: Open file
        - Ctrl+S: Save file
        - F9: Assemble code
        - F5: Run program
        - F7: Step instruction
        - F2: Reset simulator
        - F8: Toggle breakpoint
        
        ## Assembly Language Support
        
        The simulator supports standard 8086 assembly language syntax, including:
        
        - All 8086 instructions
        - Standard assembler directives
        - Labels and jumps
        - Data definitions
        
        ## Debugging Features
        
        - Set and clear breakpoints
        - Inspect memory and registers
        - Step through code one instruction at a time
        - View stack contents
        - Track CPU flags
        """
        
        docs.insert(END, documentation)
        docs.config(state=DISABLED)
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "8086 Microprocessor Simulator\n"
                             "Version 1.0\n\n"
                             "A complete 8086 simulator with full instruction set\n"
                             "support and debugging capabilities.")
    
    def exit_application(self):
        """Exit the application."""
        if self.save_if_modified():
            self.root.destroy()
    
    def run(self):
        """Run the main application loop."""
        self.root.mainloop()

# Function to start the GUI
def start_gui(cpu, memory, assembler, debugger):
    """Start the graphical user interface."""
    try:
        gui = SimulatorGUI(cpu, memory, assembler, debugger)
        gui.run()
    except Exception as e:
        import traceback
        print(f"GUI Error: {str(e)}")
        traceback.print_exc()