from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import threading
import os
import time

app = Flask(__name__)

# Global state
analysis_thread = None
menubar_process = None
is_analyzing = False
analysis_report_path = None

def run_analysis_task(start_date, end_date):
    global is_analyzing, analysis_report_path, menubar_process
    try:
        # Launch the menu bar app to show it's active in the hotbar
        # We run it detached
        menubar_process = subprocess.Popen([
            os.path.join(os.path.dirname(__file__), "venv/bin/python3"),
            os.path.join(os.path.dirname(__file__), "menubar_app.py")
        ])
        
        # Run the actual analysis process
        # We run it as a subprocess so we can capture output or just wait for it
        # Actually, running it directly is fine if we use the analyze module, but since
        # analyze.py takes args, we can call it via subprocess
        
        analyze_cmd = [
            os.path.join(os.path.dirname(__file__), "venv/bin/python3"),
            os.path.join(os.path.dirname(__file__), "analyze.py"),
            start_date,
            end_date
        ]
        
        process = subprocess.run(analyze_cmd, capture_output=True, text=True)
        print("Analysis output:", process.stdout)
        print("Analysis errors:", process.stderr)
        
        analysis_report_path = "eminence_analysis_report.md"
        
    except Exception as e:
        print(f"Analysis failed: {e}")
    finally:
        is_analyzing = False
        # Kill the menubar app when done
        if menubar_process:
            menubar_process.terminate()
            menubar_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/activate', methods=['POST'])
def activate_agent():
    global is_analyzing, analysis_thread, analysis_report_path
    
    if is_analyzing:
        return jsonify({"status": "error", "message": "Agent is already running!"}), 400
        
    data = request.json
    end_time_str = data.get('end_time', '16:00')
    
    from datetime import datetime
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    end_date = now.strftime("%Y-%m-%d") + f" {end_time_str}:00"
    
    is_analyzing = True
    analysis_report_path = None
    
    # Start analysis in background
    analysis_thread = threading.Thread(target=run_analysis_task, args=(start_date, end_date))
    analysis_thread.start()
    
    return jsonify({"status": "success", "message": "Agent Eminence activated in hotbar!"})

@app.route('/api/status', methods=['GET'])
def get_status():
    global is_analyzing, analysis_report_path
    
    if is_analyzing:
        return jsonify({"status": "analyzing"})
    elif analysis_report_path and os.path.exists(analysis_report_path):
        # We don't send the full report text back directly anymore, the UI will just show a download button
        return jsonify({"status": "complete"})
    else:
        return jsonify({"status": "idle"})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    if os.path.exists("progress.log"):
        with open("progress.log", "r") as f:
            return jsonify({"logs": f.read()})
    return jsonify({"logs": ""})

@app.route('/api/download', methods=['GET'])
def download_dossier():
    global analysis_report_path
    if analysis_report_path and os.path.exists(analysis_report_path):
        return send_file(analysis_report_path, as_attachment=True, download_name="eminence_dossier.md")
    return "No report generated yet", 404

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)
