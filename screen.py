import tkinter as tk
from tkinter import simpledialog
import sys

class RectangleSelector:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Make window semi-transparent
        self.root.configure(background='grey')
        
        # Make sure this window stays on top
        self.root.attributes('-topmost', True)
        
        # Create a canvas that covers the screen
        self.canvas = tk.Canvas(root, bg='grey')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables for rectangle coordinates
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind key events
        self.root.bind("<Return>", self.on_enter)
        self.root.bind("<Escape>", self.on_escape)
        
        # Store coordinates
        self.final_coords = None
    
    def on_press(self, event):
        # Start drawing rectangle
        self.start_x = event.x
        self.start_y = event.y
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline='red', width=2
        )
    
    def on_drag(self, event):
        # Update rectangle as mouse moves
        if self.current_rect:
            self.canvas.coords(
                self.current_rect, 
                self.start_x, self.start_y, event.x, event.y
            )
    
    def on_release(self, event):
        # Complete rectangle on mouse release
        if self.current_rect:
            self.canvas.coords(
                self.current_rect, 
                self.start_x, self.start_y, event.x, event.y
            )
    
    def on_enter(self, event):
        # When Enter is pressed, return coords and exit
        if self.current_rect:
            coords = self.canvas.coords(self.current_rect)
            
            # Calculate left, upper, right, lower coords format
            # left = minimum x value
            left = min(coords[0], coords[2])
            # upper = minimum y value (since y increases downward in tkinter)
            upper = min(coords[1], coords[3])
            # right = maximum x value
            right = max(coords[0], coords[2])
            # lower = maximum y value
            lower = max(coords[1], coords[3])
            
            # Store as (left, upper, right, lower) format
            self.final_coords = (int(left), int(upper), int(right), int(lower))
            self.root.quit()
    
    def on_escape(self, event):
        # Cancel and exit
        self.root.quit()

def main():
    try:
        root = tk.Tk()
        root.title("Rectangle Selector")
        
        # Hide the default Tkinter window
        root.withdraw()
        
        # Show a simple message about what to do
        simpledialog.messagebox.showinfo(
            "Rectangle Selector", 
            "Click and drag to select a rectangle.\n"
            "Press Enter to confirm or Escape to cancel."
        )
        
        # Create and show our selector window
        root.deiconify()
        selector = RectangleSelector(root)
        
        root.mainloop()
        
        # Get coordinates and print them
        if selector.final_coords:
            # Output in the requested tuple format (left, upper, right, lower)
            print(selector.final_coords)
        else:
            print("Selection cancelled")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Ensure application exits cleanly
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()