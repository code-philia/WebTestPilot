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
        elif self.path.startswith("/workspace-stats/"):
            workspace = self.path.split("/")[-1]
            self.get_workspace_stats(workspace)
        else:
            super().do_GET()

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
                        stats = self.calculate_workspace_stats(workspace_name)
                        workspaces.append({"name": workspace_name, "stats": stats})

            self.send_json_response({"workspaces": workspaces})
        except Exception as e:
            self.send_error_response(str(e))

    def get_workspace_stats(self, workspace):
        try:
            stats = self.calculate_workspace_stats(workspace)
            self.send_json_response(stats)
        except Exception as e:
            self.send_error_response(str(e))

    def calculate_workspace_stats(self, workspace):
        workspace_dir = self.server_dir / "data" / "splits" / workspace
        stats = self._initialize_stats()

        if not workspace_dir.exists():
            return stats

        url_to_app = self._load_issues_and_map_urls(workspace_dir, stats)
        self._count_annotations(workspace_dir, url_to_app, stats)
        self._calculate_final_stats(stats)

        return stats

    def _initialize_stats(self):
        return {
            "total_issues": 0,
            "annotated_issues": 0,
            "remaining_issues": 0,
            "progress_percentage": 0,
            "progress_by_app": {},
        }

    def _load_issues_and_map_urls(self, workspace_dir, stats):
        applications = ["bookstack", "indico", "invoiceninja", "prestashop"]
        url_to_app = {}

        for app in applications:
            app_file = workspace_dir / f"{app}.json"
            if not app_file.exists():
                stats["progress_by_app"][app] = {"total": 0, "annotated": 0}
                continue

            issues = self._safe_load_json(app_file)
            if not issues:
                stats["progress_by_app"][app] = {"total": 0, "annotated": 0}
                continue

            app_total = len(issues)
            stats["progress_by_app"][app] = {"total": app_total, "annotated": 0}
            stats["total_issues"] += app_total

            # Map each issue URL to its app
            for issue in issues:
                if "url" in issue:
                    url_to_app[issue["url"]] = app

        return url_to_app

    def _count_annotations(self, workspace_dir, url_to_app, stats):
        annotations_file = workspace_dir / "annotations.json"
        if not annotations_file.exists():
            return

        annotations = self._safe_load_json(annotations_file)
        if not annotations:
            return

        stats["annotated_issues"] = len(annotations)

        # Count annotated per app using exact URL matching
        for annotation in annotations:
            issue_url = annotation.get("issue_id", "")
            app = url_to_app.get(issue_url)
            if app and app in stats["progress_by_app"]:
                stats["progress_by_app"][app]["annotated"] += 1

    def _calculate_final_stats(self, stats):
        stats["remaining_issues"] = stats["total_issues"] - stats["annotated_issues"]
        if stats["total_issues"] > 0:
            stats["progress_percentage"] = round(
                (stats["annotated_issues"] / stats["total_issues"]) * 100, 1
            )

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
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, error_message):
        self.send_response(500)
        self.send_header("Content-type", "application/json")
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
