

function runGPT() {
    // Get the path to the Python script.
    var pythonScriptPath = "main.py";
  
    // Run the Python script.
    subprocess.run(["python", pythonScriptPath]);
}