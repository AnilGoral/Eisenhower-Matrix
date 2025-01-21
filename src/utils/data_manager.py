import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class DataManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
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

    def import_from_json(self, filepath: str) -> tuple[bool, str]:
        """Import tasks from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "tasks" not in data:
                return False, "Invalid file format: no tasks found"

            # Clear existing tasks if import successful
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

    def import_from_csv(self, filepath: str) -> tuple[bool, str]:
        """Import tasks from CSV file"""
        try:
            tasks = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tasks.append({
                        'id': row['ID'],
                        'quadrant': row['Quadrant'],
                        'description': row['Description'],
                        'done': row['Status'].lower() == 'done'
                    })

            if not tasks:
                return False, "No tasks found in CSV file"

            # Clear existing tasks if import successful
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