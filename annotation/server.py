import http.server
import json
import socketserver
from pathlib import Path


class AnnotationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_dir = Path(__file__).parent.resolve()
        super().__init__(*args, directory=str(self.server_dir), **kwargs)

    def do_GET(self):
        if self.path == "/workspaces":
            self.get_workspaces()
        else:
            super().do_GET()

    def end_headers(self):
        # Add no-cache headers for all JSON files
        if self.path.endswith(".json") or "?_=" in self.path:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        if self.path.startswith("/save-annotations/"):
            workspace = self.path.split("/")[-1]
            self.save_json_file("annotations.json", workspace)
        elif self.path.startswith("/save-labels/"):
            workspace = self.path.split("/")[-1]
            self.save_json_file("labels.json", workspace)

        else:
            self.send_error(404)

    def get_workspaces(self):
        try:
            splits_dir = self.server_dir / "data" / "splits"
            workspaces = []

            if splits_dir.exists():
                for workspace_dir in splits_dir.iterdir():
                    if workspace_dir.is_dir():
                        workspace_name = workspace_dir.name
                        workspaces.append({"name": workspace_name})

            self.send_json_response({"workspaces": workspaces})
        except Exception as e:
            self.send_error_response(str(e))

    def _safe_load_json(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return None

    def save_json_file(self, filename, workspace):
        try:
            data = self._parse_request_data()
            file_path = self._prepare_file_path(filename, workspace)

            self._write_json_file(file_path, data)

            self.send_json_response({"success": True})

        except Exception as e:
            self.send_error_response(str(e))

    def _parse_request_data(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode("utf-8"))

    def _prepare_file_path(self, filename, workspace):
        workspace_dir = self.server_dir / "data" / "splits" / workspace
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir / filename

    def _write_json_file(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, error_message):
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"success": False, "error": error_message}).encode()
        )

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    port = 8000

    print("🚀 Annotation Tool Server")
    print(f"📁 Serving from: {Path(__file__).parent.resolve()}")
    print(f"🌐 Open: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop")

    print()

    with socketserver.TCPServer(("", port), AnnotationHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
