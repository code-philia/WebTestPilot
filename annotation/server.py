#!/usr/bin/env python3
import http.server
import json
import socketserver
from pathlib import Path
import shutil
import os
import re
import threading
import time


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
        elif self.path == "/cleanup-backups":
            self.cleanup_all_dangling_backups()
            self.send_json_response({"success": True, "message": "Backup cleanup completed"})
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
        }

        if not workspace_dir.exists():
            return stats

        # Load all issues and create URL to app mapping
        applications = ["bookstack", "indico", "invoiceninja", "prestashop"]
        url_to_app = {}
        
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
                        
                        # Map each issue URL to its app
                        for issue in issues:
                            if "url" in issue:
                                url_to_app[issue["url"]] = app
                except:
                    stats["progress_by_app"][app] = {"total": 0, "annotated": 0}

        # Count annotated issues per app using the URL mapping
        annotations_file = workspace_dir / "annotations.json"
        if annotations_file.exists():
            try:
                with open(annotations_file, "r", encoding="utf-8") as f:
                    annotations = json.load(f)
                    stats["annotated_issues"] = len(annotations)

                    # Count annotated per app using exact URL matching
                    for annotation in annotations:
                        issue_url = annotation.get("issue_id", "")
                        if issue_url in url_to_app:
                            app = url_to_app[issue_url]
                            if app in stats["progress_by_app"]:
                                stats["progress_by_app"][app]["annotated"] += 1
            except:
                pass

        # Calculate remaining and percentage
        stats["remaining_issues"] = stats["total_issues"] - stats["annotated_issues"]
        if stats["total_issues"] > 0:
            stats["progress_percentage"] = round(
                (stats["annotated_issues"] / stats["total_issues"]) * 100, 1
            )

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

            # Clean up old backup files before creating new one
            self.cleanup_backup_files(file_path)

            # Create backup only if original file exists and is different
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                    
                    # Only create backup if data is actually different
                    if existing_data != data:
                        backup_path = file_path.with_suffix(f".json.bak")
                        shutil.copy2(file_path, backup_path)
                except (json.JSONDecodeError, FileNotFoundError):
                    # If existing file is corrupted, still create backup
                    backup_path = file_path.with_suffix(f".json.bak")
                    shutil.copy2(file_path, backup_path)

            # Write new data
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.send_json_response({"success": True})

        except Exception as e:
            self.send_error_response(str(e))

    def cleanup_backup_files(self, file_path):
        """Clean up backup files, keeping only the most recent one"""
        try:
            workspace_dir = file_path.parent
            base_name = file_path.stem
            backup_pattern = f"{base_name}.json.bak*"
            
            # Find all backup files for this specific file
            backup_files = list(workspace_dir.glob(backup_pattern))
            
            if len(backup_files) > 1:
                # Sort by modification time, newest first
                backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                
                # Keep only the newest backup, remove others
                for backup_file in backup_files[1:]:
                    try:
                        backup_file.unlink()
                    except OSError:
                        # Ignore files that can't be deleted (might be locked)
                        pass
                        
        except Exception:
            # Don't let cleanup errors break the main functionality
            pass

    def cleanup_all_dangling_backups(self):
        """Clean up all dangling .bak files that don't have corresponding main files"""
        try:
            splits_dir = self.server_dir / "data" / "splits"
            if not splits_dir.exists():
                return
                
            for workspace_dir in splits_dir.iterdir():
                if not workspace_dir.is_dir():
                    continue
                    
                for backup_file in workspace_dir.glob("*.json.bak"):
                    # Check if corresponding main file exists
                    main_file = backup_file.with_suffix('').with_suffix('.json')
                    if not main_file.exists():
                        try:
                            backup_file.unlink()
                        except OSError:
                            pass
                            
        except Exception:
            pass



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


def periodic_cleanup():
    """Run periodic cleanup every hour"""
    handler = AnnotationHandler()
    while True:
        try:
            time.sleep(3600)  # 1 hour
            handler.cleanup_all_dangling_backups()
            print("🧹 Periodic backup cleanup completed")
        except Exception as e:
            print(f"⚠️  Error during periodic cleanup: {e}")

def main():
    port = 8000

    print("🚀 Annotation Tool Server")
    print(f"📁 Serving from: {Path(__file__).parent.resolve()}")
    print(f"🌐 Open: http://localhost:{port}")
    print(f"⏹️  Press Ctrl+C to stop")
    
    # Clean up dangling backup files on startup
    handler = AnnotationHandler()
    handler.cleanup_all_dangling_backups()
    print("🧹 Cleaned up dangling backup files")
    
    # Start periodic cleanup thread
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    print("🔄 Started periodic backup cleanup (every hour)")
    print()

    with socketserver.TCPServer(("", port), AnnotationHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
