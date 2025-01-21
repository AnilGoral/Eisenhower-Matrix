import sqlite3
from typing import List, Tuple, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Create or update the tasks table with correct schema"""
        try:
            # First check if table exists and has correct schema
            self.cursor.execute("PRAGMA table_info(tasks)")
            columns = {column[1] for column in self.cursor.fetchall()}
            required_columns = {
                'id', 'quadrant', 'description', 'done',
                'created_at', 'completed_at', 'deleted'
            }
            
            # Only recreate table if missing required columns
            if not columns.issuperset(required_columns):
                # Create temporary table to save existing tasks
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks_backup (
                        id TEXT PRIMARY KEY,
                        quadrant TEXT,
                        description TEXT,
                        done BOOLEAN
                    )
                """)
                
                # Copy existing data if old table exists
                if 'tasks' in columns:
                    self.cursor.execute("""
                        INSERT INTO tasks_backup (id, quadrant, description, done)
                        SELECT id, quadrant, description, done FROM tasks
                    """)
                
                # Drop and recreate tasks table with correct schema
                self.cursor.execute("DROP TABLE IF EXISTS tasks")
                self.cursor.execute("""
                    CREATE TABLE tasks (
                        id TEXT PRIMARY KEY,
                        quadrant TEXT,
                        description TEXT,
                        done BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        deleted BOOLEAN DEFAULT 0
                    )
                """)
                
                
                # Restore data from backup
                self.cursor.execute("""
                    INSERT INTO tasks (id, quadrant, description, done)
                    SELECT id, quadrant, description, done FROM tasks_backup
                """)
                
                # Drop backup table
                self.cursor.execute("DROP TABLE IF EXISTS tasks_backup")
                
           
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")
    
   
    def add_task(self, task_id: str, quadrant: str, description: str, done: bool = False) -> bool:
        """Add a task to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO tasks (id, quadrant, description, done) VALUES (?, ?, ?, ?)",
                (task_id, quadrant, description, done)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_tasks(self, quadrant: str) -> List[Tuple]:
        return self.cursor.execute(
            "SELECT id, description, done FROM tasks WHERE quadrant=?",
            (quadrant,)
        ).fetchall()

    def update_task_status(self, task_id: str, done: bool) -> bool:
        """Update task status and set completed_at timestamp if done"""
        try:
            if done:
                self.cursor.execute("""
                    UPDATE tasks 
                    SET done = 1, 
                        completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (task_id,))
            else:
                self.cursor.execute("""
                    UPDATE tasks 
                    SET done = 0, 
                        completed_at = NULL 
                    WHERE id = ?
                """, (task_id,))
            
            self.conn.commit()
            
            # Verify the update
            self.cursor.execute("SELECT done FROM tasks WHERE id = ?", (task_id,))
            result = self.cursor.fetchone()
            print(f"Task {task_id} status updated to {done}, verified value: {result[0] if result else 'not found'}")
            
            return True
        except sqlite3.Error as e:
            print(f"Database error in update_task_status: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        try:
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def update_task_description(self, task_id: str, description: str) -> bool:
        try:
            self.cursor.execute(
                "UPDATE tasks SET description=? WHERE id=?",
                (description, task_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def move_task(self, task_id: str, new_quadrant: str) -> bool:
        try:
            self.cursor.execute(
                "UPDATE tasks SET quadrant=? WHERE id=?",
                (new_quadrant, task_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from the database"""
        try:
            self.cursor.execute("SELECT id, quadrant, description, done FROM tasks")
            tasks = []
            for row in self.cursor.fetchall():
                tasks.append({
                    'id': row[0],
                    'quadrant': row[1],
                    'description': row[2],
                    'done': bool(row[3])
                })
            return tasks
        except sqlite3.Error:
            return []

    def clear_all_tasks(self) -> bool:
        """Clear all tasks from the database"""
        try:
            self.cursor.execute("DELETE FROM tasks")
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get all statistics"""
        stats = {
            'per_quadrant': {},
            'overview': {
                'total_created': 0,
                'total_completed': 0,
                'current_active': 0
            }
        }

        try:
            # Get quadrant statistics
            self.cursor.execute("""
                SELECT 
                    quadrant,
                    COUNT(*) as total_created,
                    SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) as active,
                    AVG(CASE 
                        WHEN done = 1 
                        THEN ROUND((julianday(completed_at) - julianday(created_at)) * 24 * 60, 2)
                        ELSE NULL 
                    END) as avg_completion_minutes
                FROM tasks
                WHERE deleted = 0 OR deleted IS NULL
                GROUP BY quadrant
            """)
            
            for row in self.cursor.fetchall():
                quadrant = row[0]
                total = row[1]
                completed = row[2] or 0
                active = row[3] or 0
                avg_time = row[4]
                
                stats['per_quadrant'][quadrant] = {
                    'total_created': total,
                    'completed': completed,
                    'active_tasks': active,
                    'avg_completion_time': avg_time,
                    'completion_rate': (completed / total * 100) if total > 0 else 0
                }

            # Get overview statistics
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_created,
                    SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as total_completed,
                    SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) as current_active
                FROM tasks
                WHERE deleted = 0 OR deleted IS NULL
            """)
            
            row = self.cursor.fetchone()
            if row:
                stats['overview']['total_created'] = row[0] or 0
                stats['overview']['total_completed'] = row[1] or 0
                stats['overview']['current_active'] = row[2] or 0

            return stats
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return stats



    def __del__(self):
        if self.conn:
            self.conn.close() 