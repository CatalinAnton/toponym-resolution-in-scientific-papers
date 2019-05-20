// document.getElementById("submit-button").addEventListener("click", function () {
//     const textarea_content = document.getElementById('textarea').value;
//     let data = {"text": textarea_content};
//     console.log(data);
//     url = 'http://localhost:8880/text';
//
//     fetch(url, {
//         method: "POST",
//         body: JSON.stringify({"text": textarea_content})
//     }).then(res => {
//         console.log("Request complete! response:", res);
//     })
//     .catch(error => console.error(error));
// });

data = {}
const textarea_content = document.getElementById('textarea').value;
data["text"] = textarea_content;

$.ajax({
    type: "POST",
    url: "http://localhost:8880/text",
    // The key needs to match your method's input parameter (case-sensitive).
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) {
        alert(data);
    },
    failure: function (errMsg) {
        alert(errMsg);
    }
});
//
// var form = document.getElementById("form")
//
// form.onsubmit = function (e) {
//     // stop the regular form submission
//     e.preventDefault();
//
//     // collect the form data while iterating over the inputs
//     var data = {};
//     for (var i = 0, ii = form.length; i < ii; ++i) {
//         var input = form[i];
//         if (input.name) {
//             data[input.name] = input.value;
//         }
//     }
//
//     const textarea_content = document.getElementById('textarea').value;
//     data["text"] = textarea_content;
//
//     // construct an HTTP request
//     var xhr = new XMLHttpRequest();
//     url = 'http://localhost:8880/text';
//     xhr.open(form.method, url, true);
//     xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
//
//     // send the collected data as JSON
//     xhr.send(JSON.stringify(data));
//
//     xhr.onloadend = function () {
//         // done
//     };
// };