let form = document.getElementById("form")

form.onsubmit = function (e) {
    // stop the regular form submission
    e.preventDefault();

    // collect the form data while iterating over the inputs
    let data = {};
    for (var i = 0, ii = form.length; i < ii; ++i) {
        var input = form[i];
        if (input.name) {
            data[input.name] = input.value;
        }
    }

    const textarea_content = document.getElementById('textarea').value;
    data["text"] = textarea_content;

    // construct an HTTP request
    let xhr = new XMLHttpRequest();
    let url = 'http://localhost:8880/text';
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

    // send the collected data as JSON
    xhr.send(JSON.stringify(data));

    xhr.onloadend = function () {
        let obj = JSON.parse(this.responseText);
        let pretty = JSON.stringify(obj, undefined, 4);
        document.getElementById('textarea_result').value = pretty;
    };
};