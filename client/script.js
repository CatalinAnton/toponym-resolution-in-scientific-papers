document.getElementById("form").addEventListener("click", function () {
    const textarea_content = document.getElementById('textarea').value;
    let data = {text_input: textarea_content};
    url = 'https://localhost:80/end-point-server-url';

    fetch(url, {
        method: "POST",
        body: JSON.stringify(data)
    }).then(res => {
        console.log("Request complete! response:", res);
    })
    .catch(error => console.error(error));
});