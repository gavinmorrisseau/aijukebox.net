function runGPT() {
    // Get the path to the Python script.
    var pythonScriptPath = "/src/GPT.py";
  
    // Run the Python script.
    subprocess.run(["python", pythonScriptPath]);
  }