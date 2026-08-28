"""
Top-level entrypoint to execute the Higher Education ROI Analytics Pipeline.
"""
from src.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline(force_recompute=False)
