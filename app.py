#!/usr/bin/env python3
"""
8086 Simulator - Web Interface
A Flask-based web interface for the 8086 microprocessor simulator.
"""

import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from cpu import CPU
from memory import Memory
from assembler import Assembler
from debugger import Debugger

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")  # For flash messages and sessions

# Initialize simulator components (these will be initialized per session later)
memory = Memory()
cpu = CPU(memory)
assembler = Assembler(cpu, memory)
debugger = Debugger(cpu, memory, None)  # UI is None for now as we're using the web interface

# Import profiler if available
try:
    from profiler import create_profiler
    PROFILER_AVAILABLE = True
except ImportError:
    PROFILER_AVAILABLE = False

# Try to import the fix_segment_handling function
try:
    from fix_instructions import fix_segment_handling
    FIXED_SEGMENTS_AVAILABLE = True
except ImportError:
    FIXED_SEGMENTS_AVAILABLE = False


@app.route('/')
def index():
    """Render the main page"""
    register_state = cpu.get_register_state()
    flag_state = cpu.get_flag_state()
    
    # Get memory dump for display
    code_start = 0x100  # Default CODE segment start
    code_size = 256
    data_start = 0x200  # Default DATA segment start
    data_size = 256
    stack_start = 0x300  # Default STACK segment start
    stack_size = 256
    
    code_memory = memory.dump(code_start, code_size)
    data_memory = memory.dump(data_start, data_size)
    stack_memory = memory.dump(stack_start, stack_size)
    
    # Sample programs for quick loading
    sample_programs = [
        {"name": "Hello World", "path": "sample_programs/hello.asm"},
        {"name": "Simple Test", "path": "sample_programs/test_simple.asm"},
        {"name": "Performance Test", "path": "sample_programs/performance_test.asm"}
    ]
    
    return render_template('index.html', 
                          registers=register_state,
                          flags=flag_state,
                          code_memory=code_memory,
                          data_memory=data_memory,
                          stack_memory=stack_memory,
                          sample_programs=sample_programs)


@app.route('/reset', methods=['POST'])
def reset_simulator():
    """Reset the simulator to initial state"""
    cpu.reset()
    memory.reset()
    flash('Simulator has been reset', 'success')
    return redirect(url_for('index'))


@app.route('/load_program', methods=['POST'])
def load_program():
    """Load a program from the selected file or code input"""
    # Check if a file was uploaded
    if 'program_file' in request.files and request.files['program_file'].filename:
        file = request.files['program_file']
        
        # Save the file temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)
        
        # Reset the CPU and memory before loading
        cpu.reset()
        memory.reset()
        
        try:
            # Use fixed segment handling if available
            if FIXED_SEGMENTS_AVAILABLE:
                fix_segment_handling(assembler, temp_path)
            else:
                assembler.load_program(temp_path)
            
            flash(f'Program {file.filename} loaded successfully', 'success')
        except Exception as e:
            flash(f'Error loading program: {str(e)}', 'danger')
        
        # Clean up the temporary file
        os.remove(temp_path)
    
    # Check if code was entered in the textarea
    elif request.form.get('code_input'):
        code = request.form.get('code_input')
        
        # Save the code to a temporary file
        temp_path = os.path.join('temp', 'code_input.asm')
        os.makedirs('temp', exist_ok=True)
        
        with open(temp_path, 'w') as f:
            f.write(code)
        
        # Reset the CPU and memory before loading
        cpu.reset()
        memory.reset()
        
        try:
            # Use fixed segment handling if available
            if FIXED_SEGMENTS_AVAILABLE:
                fix_segment_handling(assembler, temp_path)
            else:
                assembler.load_program(temp_path)
            
            flash('Program loaded successfully from input', 'success')
        except Exception as e:
            flash(f'Error loading program: {str(e)}', 'danger')
        
        # Clean up the temporary file
        os.remove(temp_path)
    
    # Check if a sample program was selected
    elif request.form.get('sample_program'):
        sample_path = request.form.get('sample_program')
        
        if os.path.exists(sample_path):
            # Reset the CPU and memory before loading
            cpu.reset()
            memory.reset()
            
            try:
                # Use fixed segment handling if available
                if FIXED_SEGMENTS_AVAILABLE:
                    fix_segment_handling(assembler, sample_path)
                else:
                    assembler.load_program(sample_path)
                
                flash(f'Sample program {os.path.basename(sample_path)} loaded successfully', 'success')
            except Exception as e:
                flash(f'Error loading sample program: {str(e)}', 'danger')
        else:
            flash(f'Sample program file not found: {sample_path}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/execute', methods=['POST'])
def execute_program():
    """Execute the loaded program"""
    try:
        # Initialize profiler if available
        profiler = None
        if PROFILER_AVAILABLE and request.form.get('enable_profiling') == 'on':
            profiler = create_profiler(cpu, memory)
            cpu.set_profiler(profiler)
            memory.set_profiler(profiler)
            profiler.start_profiling()
        
        # Get max instructions parameter
        try:
            max_instructions = int(request.form.get('max_instructions', 1000))
        except ValueError:
            max_instructions = 1000  # Default if invalid input
        
        # Run the program
        cpu.run(max_instructions=max_instructions)
        
        # Get profiler results if available
        profiler_results = None
        if profiler:
            profiler.stop_profiling()
            profiler_results = profiler.generate_summary_report()
            
            # Store detailed results in session if requested
            if request.form.get('detailed_profiling') == 'on':
                session['detailed_profiling'] = profiler.generate_detailed_report()
            
            # Remove profiler from CPU and memory
            cpu.set_profiler(None)
            memory.set_profiler(None)
        
        flash('Program executed successfully', 'success')
        
        # If profiling was enabled, include the results
        if profiler_results:
            flash('Profiling results available', 'info')
            session['profiler_results'] = profiler_results
        
        return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error executing program: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/step', methods=['POST'])
def step_instruction():
    """Execute a single instruction"""
    try:
        debugger.step_instruction()
        flash('Executed one instruction', 'success')
    except Exception as e:
        flash(f'Error stepping instruction: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/toggle_breakpoint', methods=['POST'])
def toggle_breakpoint():
    """Toggle a breakpoint at the specified address"""
    try:
        address = int(request.form.get('breakpoint_address', '0'), 16)
        debugger.toggle_breakpoint(address)
        flash(f'Toggled breakpoint at address 0x{address:04X}', 'success')
    except ValueError:
        flash('Invalid address format. Use hexadecimal (e.g., 0100)', 'danger')
    except Exception as e:
        flash(f'Error toggling breakpoint: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/run_to_breakpoint', methods=['POST'])
def run_to_breakpoint():
    """Run the program until a breakpoint is hit"""
    try:
        debugger.run_to_breakpoint()
        flash('Execution stopped at breakpoint or program end', 'success')
    except Exception as e:
        flash(f'Error running to breakpoint: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/profiler_results')
def profiler_results():
    """Show the profiler results"""
    results = session.get('profiler_results', 'No profiling results available')
    detailed_results = session.get('detailed_profiling', None)
    
    return render_template('profiler_results.html', 
                           results=results, 
                           detailed_results=detailed_results)


@app.route('/api/register_state')
def api_register_state():
    """API endpoint for getting the current register state"""
    register_state = cpu.get_register_state()
    flag_state = cpu.get_flag_state()
    
    return jsonify({
        'registers': register_state,
        'flags': flag_state
    })


@app.route('/api/memory')
def api_memory():
    """API endpoint for getting memory contents"""
    start = request.args.get('start', 0, type=int)
    length = request.args.get('length', 256, type=int)
    
    # Limit the request to reasonable size
    if length > 4096:
        length = 4096
    
    memory_dump = memory.dump(start, length)
    
    return jsonify({
        'start': start,
        'length': length,
        'memory': memory_dump
    })


if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)