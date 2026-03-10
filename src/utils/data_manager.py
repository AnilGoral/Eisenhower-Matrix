import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class DataManager:
    def __init__(self, db_manager, app_data_dir: str = None):
        self.db_manager = db_manager
        if app_data_dir:
            self.export_dir = Path(app_data_dir) / 'exports'
        else:
            self.export_dir = Path.home() / '.eisenhower_matrix' / 'exports'
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_to_json(self, filepath: str = None) -> str:
        """Export all tasks to JSON format"""
        tasks = self.db_manager.get_all_tasks()
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "tasks": tasks
        }

        if not filepath:
            filepath = self.export_dir / f"eisenhower_matrix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def import_from_json(self, filepath: str) -> tuple:
        """Import tasks from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "tasks" not in data:
                return False, "Invalid file format: no tasks found"

            # Validate all tasks BEFORE clearing existing data
            required_fields = {"id", "quadrant", "description", "done"}
            for i, task in enumerate(data["tasks"]):
                missing = required_fields - set(task.keys())
                if missing:
                    return False, f"Task {i+1} is missing fields: {', '.join(missing)}"

            # Clear existing tasks only after validation passes
            self.db_manager.clear_all_tasks()

            # Import tasks
            for task in data["tasks"]:
                self.db_manager.add_task(
                    task["id"],
                    task["quadrant"],
                    task["description"],
                    task["done"]
                )

            return True, f"Successfully imported {len(data['tasks'])} tasks"
        except Exception as e:
            return False, f"Error importing data: {str(e)}"

    def export_to_csv(self, filepath: str = None) -> str:
        """Export all tasks to CSV format"""
        tasks = self.db_manager.get_all_tasks()

        if not filepath:
            filepath = self.export_dir / f"eisenhower_matrix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['ID', 'Quadrant', 'Description', 'Status'])
            # Write tasks
            for task in tasks:
                writer.writerow([
                    task['id'],
                    task['quadrant'],
                    task['description'],
                    'Done' if task['done'] else 'Pending'
                ])

        return str(filepath)

    def import_from_csv(self, filepath: str) -> tuple:
        """Import tasks from CSV file"""
        try:
            tasks = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Validate headers
                required_headers = {'ID', 'Quadrant', 'Description', 'Status'}
                if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
                    missing = required_headers - set(reader.fieldnames or [])
                    return False, f"CSV missing required columns: {', '.join(missing)}"

                for row in reader:
                    task_id = row['ID'].strip()
                    if not self._is_valid_uuid(task_id):
                        return False, f"Invalid task ID format: {task_id}"
                    tasks.append({
                        'id': task_id,
                        'quadrant': row['Quadrant'],
                        'description': row['Description'],
                        'done': row['Status'].lower() == 'done'
                    })

            if not tasks:
                return False, "No tasks found in CSV file"

            # Clear existing tasks only AFTER full validation passes
            self.db_manager.clear_all_tasks()

            # Import tasks
            for task in tasks:
                self.db_manager.add_task(
                    task['id'],
                    task['quadrant'],
                    task['description'],
                    task['done']
                )

            return True, f"Successfully imported {len(tasks)} tasks"
        except Exception as e:
            return False, f"Error importing data: {str(e)}"

    @staticmethod
    def _is_valid_uuid(value: str) -> bool:
        """Check if a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False