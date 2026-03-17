import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QTextEdit, QProgressBar, QLabel)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# 🏗️ Worker Thread to handle C-backend execution without freezing the GUI
class OspreyWorker(QThread):
    progress_update = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, binary_path, flag, target_file):
        super().__init__()
        self.binary_path = binary_path
        self.flag = flag
        self.target_file = target_file

    def run(self):
        try:
            # Calculate file size for progress tracking logic [cite: 122, 215]
            file_size = os.path.getsize(self.target_file)
            
            # Execute the compiled C backend (osprey-backend)
            # We use the flags defined in sigtool.c like --info, --verify, or --sha256 [cite: 309, 444, 121]
            cmd = [self.binary_path, self.flag, self.target_file]
            
            # Simulate progress for hashing large files based on FILEBUFF logic [cite: 212, 216]
            # In a production environment, you would pipe stdout to track real-time offsets
            for i in range(1, 101):
                self.msleep(20) # Simulate processing time
                self.progress_update.emit(i)

            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                self.result_ready.emit(process.stdout)
            else:
                self.error_occurred.emit(process.stderr)
        except Exception as e:
            self.error_occurred.emit(str(e))

# 🖥️ Main Fedora GUI Window
class OspreyView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Osprey - ClamAV Analysis Suite")
        self.setMinimumSize(700, 500)
        self.backend_path = "/usr/bin/osprey-backend" # Defined in your .spec file

        # Layout Setup
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to analyze. Select an operation below:")
        layout.addWidget(self.status_label)

        # Output Display
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace;")
        layout.addWidget(self.output_area)

        # Progress Bar [Engineering Challenge: Responsive Hashing]
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Control Buttons 
        self.btn_hash = QPushButton("Generate SHA256 Hash")
        self.btn_hash.clicked.connect(lambda: self.launch_worker("--sha256"))
        layout.addWidget(self.btn_hash)

        self.btn_verify = QPushButton("Verify Digital Signature")
        self.btn_verify.clicked.connect(lambda: self.launch_worker("--verify"))
        layout.addWidget(self.btn_verify)

        self.btn_info = QPushButton("Inspect CVD Database")
        self.btn_info.clicked.connect(lambda: self.launch_worker("--info"))
        layout.addWidget(self.btn_info)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def launch_worker(self, flag):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File for Analysis")
        if not file_path:
            return

        # Reset UI for new task
        self.output_area.clear()
        self.progress_bar.setValue(0)
        self.set_controls_enabled(False)
        self.status_label.setText(f"Processing: {os.path.basename(file_path)}...")

        # Initialize and start background thread
        self.worker = OspreyWorker(self.backend_path, flag, file_path)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.result_ready.connect(self.handle_success)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(lambda: self.set_controls_enabled(True))
        self.worker.start()

    def handle_success(self, text):
        self.output_area.setText(text)
        self.status_label.setText("Analysis Complete.")

    def handle_error(self, text):
        self.output_area.setText(f"ERROR:\n{text}")
        self.status_label.setText("Analysis Failed.")

    def set_controls_enabled(self, enabled):
        self.btn_hash.setEnabled(enabled)
        self.btn_verify.setEnabled(enabled)
        self.btn_info.setEnabled(enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply Fedora-friendly styling (optional)
    app.setStyle("Fusion")
    window = OspreyView()
    window.show()
    sys.exit(app.exec())
