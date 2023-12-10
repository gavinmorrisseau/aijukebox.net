// Import required modules
const express = require('express');
const markdown = require('markdown-it');

// Create an instance of Express
const app = express();

// Create an instance of Markdown parser
const md = markdown();

// Define routes
app.get('/', (req, res) => {
    const markdownText = `
        # Hello, world!
        
        This is a **Markdown** block.
        
        - Item 1
        - Item 2
        - Item 3
    `;
    
    const html = md.render(markdownText);
    res.send(html);
});

// Start the server
const port = 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
