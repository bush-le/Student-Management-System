"""Helper utilities for running heavy operations on background threads"""
import threading
from typing import Callable, Any
import tkinter as tk

class BackgroundTask:
    """Run a task on a background thread without blocking UI"""
    
    def __init__(self, func: Callable, on_complete: Callable = None, on_error: Callable = None, tk_root=None):
        """
        Args:
            func: Function to run in background
            on_complete: Callback when complete (receives result)
            on_error: Callback on error (receives exception)
            tk_root: tkinter root for thread-safe UI updates
        """
        self.func = func
        self.on_complete = on_complete
        self.on_error = on_error
        self.tk_root = tk_root
        self.thread = None
    
    def start(self):
        """Start the background task"""
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        """Execute the function and call appropriate callback"""
        try:
            result = self.func()
            if self.on_complete:
                # Schedule callback on main thread if tk_root available
                if self.tk_root:
                    self.tk_root.after(0, lambda: self._safe_callback(self.on_complete, result))
                else:
                    self.on_complete(result)
        except Exception as e:
            if self.on_error:
                if self.tk_root:
                    self.tk_root.after(0, lambda: self._safe_callback(self.on_error, e))
                else:
                    self.on_error(e)
            else:
                print(f"❌ Background task error: {e}")
    
    def _safe_callback(self, callback, arg):
        """Safely execute callback with error handling"""
        try:
            callback(arg)
        except tk.TclError:
            # Widget destroyed, ignore
            pass
        except Exception as e:
            print(f"❌ Callback error: {e}")

def run_in_background(func: Callable, on_complete: Callable = None, on_error: Callable = None, tk_root=None):
    """Convenience function to run a task in background"""
    task = BackgroundTask(func, on_complete, on_error, tk_root)
    task.start()
    return task
