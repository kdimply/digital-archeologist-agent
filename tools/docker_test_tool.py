import docker
import logging
import os
import tarfile
import io
import glob

logger = logging.getLogger("LogicFlow.Docker")

def run_isolated_test(code_snippet, file_name="solution.py"):
    """
    Final Flattened Workspace Sandbox.
    Ensures headers and source files are in the same directory inside Docker.
    """
    client = docker.from_env()
    container = None
    
    # FLATTEN: Get just the filename (e.g., 'utils.c' instead of 'demo/utils.c')
    short_name = os.path.basename(file_name)
    ext = short_name.split('.')[-1]
    
    # 1. UPDATED COMMANDS: Use flattened short_name and compile all local C files
    commands = {
        'py': ['python', short_name],
        'js': ['node', short_name],
        'cpp': ['bash', '-c', f'g++ -I. *.cpp -o out && ./out'], 
        'c': ['bash', '-c', f'gcc -I. *.c -o out && ./out']
    }
    
    if ext == 'py': 
        image = "python:3.12-slim"
    elif ext in ['c', 'cpp', 'h']: 
        image = "gcc:latest"
    elif ext == 'js': 
        image = "node:20-slim"
    else:
        image = "python:3.12-slim"

    try:
        logger.info(f"Spinning up {image} sandbox for {short_name}...")
        
        container = client.containers.run(
            image=image,
            command="sleep 60", 
            detach=True,
            remove=True,
            network_disabled=True,
            mem_limit="512m" 
        )

        # 2. FLATTENED WORKSPACE SYNC
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # First, add the AI-generated code (using the short_name)
            content_bytes = code_snippet.encode('utf-8')
            file_info = tarfile.TarInfo(name=short_name)
            file_info.size = len(content_bytes)
            tar.addfile(tarinfo=file_info, fileobj=io.BytesIO(content_bytes))
            
            # Second, find all headers and source files in 'demo/'
            # We use arcname to remove the 'demo/' prefix inside the container
            search_path = os.path.join("demo", "*.[ch]*")
            dependency_files = glob.glob(search_path)
            
            for dep_path in dependency_files:
                dep_name = os.path.basename(dep_path)
                # Avoid adding the primary file twice
                if dep_name != short_name:
                    tar.add(dep_path, arcname=dep_name)
                    logger.info(f"Flattened dependency added: {dep_name}")
        
        tar_stream.seek(0)
        container.put_archive(path="/", data=tar_stream)

        # 3. EXECUTE
        logger.info(f"Running {ext} execution in flattened workspace...")
        exec_log = container.exec_run(
            cmd=commands.get(ext, ['python', short_name]),
            workdir="/"
        )

        exit_code = exec_log.exit_code
        logs = exec_log.output.decode("utf-8")
        
        container.stop()
        logger.info(f"Verification complete. Exit Code: {exit_code}")
        
        return (exit_code == 0), logs

    except Exception as e:
        logger.error(f"Sandbox Failure: {e}")
        if container:
            try: container.kill()
            except: pass
        return False, f"Sandbox Error: {e}"