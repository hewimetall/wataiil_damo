function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}


async function postData(url = "/post", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "put",
    mode: "cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    redirect: "follow",
    referrerPolicy: "no-referrer",
    body: JSON.stringify(data),
  });
  return await response.json(); // parses JSON response into native JavaScript objects
}

async function postData(url = "/post", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "put",
    mode: "cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    redirect: "follow",
    referrerPolicy: "no-referrer",
    body: JSON.stringify(data),
  });
  return await response.json(); // parses JSON response into native JavaScript objects
}

function annotation(elem, url, load_data) {
  var r = Recogito.init({
    content: document.getElementById(elem), // ID or DOM element
    widgets: [{ widget: "COMMENT" }],
  });
  var ll;
  fetch(url, {
    method: "get",
    mode: "cors",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
    },
  })
  .then(response => {
      return response.json() //Convert response to JSON
  })
  .then(data => {
  ll = data;
       r.loadAnnotations(data)
  })
    r.loadAnnotations(url)
    console.log(ll)
  // Add an event handler
  r.on("createAnnotation", async (annotation) => {
    annotation["event"] = 'createAnnotation';
    await postData(url, annotation);
  });
  r.on("updateAnnotation", async (annotation, previous) => {
    annotation["event"] = 'updateAnnotation';
    annotation['previous']  = previous;
    await postData(url, annotation);
  });
          // Wire the Add/Update/Remove buttons
//          !TODO: Доделать очистку страницы
//        document
//          .getElementById("add-annotation")
//          .addEventListener("click", function () {
//            r.addAnnotation(myAnnotation);
//          });
//
//        document
//          .getElementById("update-annotation")
//          .addEventListener("click", function () {
//            r.addAnnotation(
//            );
//          });
//
//        document
//          .getElementById("remove-annotation")
//          .addEventListener("click", function () {
//            r.removeAnnotation(myAnnotation);
//          });

        // Switch annotation mode (annotation/relationships)
        var annotationMode = "ANNOTATION"; // or 'RELATIONS'

        var toggleModeBtn = document.getElementById("wagtail-toggle-mode");
        toggleModeBtn.addEventListener("click", function () {
          if (annotationMode === "ANNOTATION") {
            toggleModeBtn.innerHTML = "MODE: RELATIONS";
            annotationMode = "RELATIONS";
          } else {
            toggleModeBtn.innerHTML = "MODE: ANNOTATION";
            annotationMode = "ANNOTATION";
          }

          r.setMode(annotationMode);
        });
      };
