import asyncio

def run_async(coro):
    """
    Runs an async function in a Streamlit-friendly way.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)