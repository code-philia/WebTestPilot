#!/usr/bin/env python3
import http.server
import json
import socketserver
from pathlib import Path
import shutil
import os
import re


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
        elif self.path.startswith("/update-metadata/"):
            workspace = self.path.split("/")[-1]
            self.update_metadata(workspace)
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
        stats = {
            "total_issues": 0,
            "annotated_issues": 0,
            "remaining_issues": 0,
            "progress_percentage": 0,
            "progress_by_app": {},
            "last_activity": None,
            "last_annotated_by": None,
        }

        if not workspace_dir.exists():
            return stats

        # Count total issues per application
        applications = ["bookstack", "indico", "invoiceninja", "prestashop"]
        for app in applications:
            app_file = workspace_dir / f"{app}.json"
            if app_file.exists():
                try:
                    with open(app_file, "r", encoding="utf-8") as f:
                        issues = json.load(f)
                        app_total = len(issues)
                        stats["progress_by_app"][app] = {
                            "total": app_total,
                            "annotated": 0,
                        }
                        stats["total_issues"] += app_total
                except:
                    stats["progress_by_app"][app] = {"total": 0, "annotated": 0}

        # Count annotated issues
        annotations_file = workspace_dir / "annotations.json"
        if annotations_file.exists():
            try:
                with open(annotations_file, "r", encoding="utf-8") as f:
                    annotations = json.load(f)
                    stats["annotated_issues"] = len(annotations)

                    # Count annotated per app (approximate)
                    for annotation in annotations:
                        issue_url = annotation.get("issue_id", "")
                        for app in applications:
                            if app.lower() in issue_url.lower():
                                if app in stats["progress_by_app"]:
                                    stats["progress_by_app"][app]["annotated"] += 1
                                break
            except:
                pass

        # Calculate remaining and percentage
        stats["remaining_issues"] = stats["total_issues"] - stats["annotated_issues"]
        if stats["total_issues"] > 0:
            stats["progress_percentage"] = round(
                (stats["annotated_issues"] / stats["total_issues"]) * 100, 1
            )

        # Load metadata
        metadata_file = workspace_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    stats["last_activity"] = metadata.get("last_activity")
                    stats["last_annotated_by"] = metadata.get("last_annotated_by")
            except:
                pass

        return stats

    def save_json_file(self, filename, workspace):
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            # Save to workspace folder
            workspace_dir = self.server_dir / "data" / "splits" / workspace
            workspace_dir.mkdir(parents=True, exist_ok=True)
            file_path = workspace_dir / filename

            # Create backup
            if file_path.exists():
                backup_path = file_path.with_suffix(f".json.bak")
                shutil.copy2(file_path, backup_path)

            # Write new data
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.send_json_response({"success": True})

        except Exception as e:
            self.send_error_response(str(e))

    def update_metadata(self, workspace):
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            metadata = json.loads(post_data.decode("utf-8"))

            # Save metadata to workspace folder
            workspace_dir = self.server_dir / "data" / "splits" / workspace
            workspace_dir.mkdir(parents=True, exist_ok=True)
            metadata_file = workspace_dir / "metadata.json"

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.send_json_response({"success": True})

        except Exception as e:
            self.send_error_response(str(e))

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
    print(f"⏹️  Press Ctrl+C to stop")
    print()

    with socketserver.TCPServer(("", port), AnnotationHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
