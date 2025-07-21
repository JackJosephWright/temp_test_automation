"""
Temp Test Automation - Main Module

a simple hello world script to test the automation setup
"""


def hello_world():
    """
    Print a hello world message.
    """
    print("Hello, world!")
    return "Hello, world!"

def run_pipeline():
    """
    Main pipeline entrypoint"""

    print('starting temp_test_automation pipeline')
    result = hello_world()
    print("pipeline completed successfully with result:", result)
    return result


if __name__ == "__main__":
    run_pipeline()