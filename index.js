

function runGPT(input) {
    var jqXHR = $.ajax({
        type: "POST",
        url: "/main.py",
        async: false,
        data: { param: input }
    });

    return jqXHR.responseText;
}

// do something with the response
response= runPyScript('data to process');
console.log(response);