"""Vision-related utilities and analysis hooks.

Currently a placeholder class used to integrate GUI vision or screenshot-based
analysis in the future. Kept minimal so tests and imports succeed.
"""

class VisionInterface:
    """Placeholder interface for vision-based GUI analysis or screenshot heuristics."""
    def analyze_gui(self, image_path: str):
        """Analyze a screenshot at `image_path` and return a simple status string."""
        return "VISION_NOT_IMPLEMENTED"
