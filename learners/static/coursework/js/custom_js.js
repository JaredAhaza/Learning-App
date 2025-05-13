function welcome(){
    alert("This is the FrontEnd theme created and designed by myself which was done as my semester project in my university by using local storage.  But soon i will convert into a complete dashboard by attaching DataBase and using PHP.")
}
/*//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////------------------------------------------------Toggle  -----------------------------------------------------
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////*/

function toggle(){
    var logoImg = document.getElementById("logo-img");
    var topbar = document.getElementById("top-bar");
    var toggClose = document.getElementById("togg-close");
    var logohead = document.getElementById("logo-head");
    var sidenav = document.getElementById("side-nav")
    var element = document.getElementById("navbar");
    var add = document.getElementById("togg-open");

    if(element.style.display === "none"){

        element.style.display = "block";
        sidenav.style.width = "100%";
        logohead.style.display = "block";
        toggClose.style.fontSize = "2em";
        topbar.style.height = "0px";
        // topbar.style.transition = "all 0.75s ease-in-out;"
        logoImg.style.width = "60%";
        add.classList.remove("fa-bars");
    add.classList.add("fa-xmark");
    }
    else{
        element.style.display = "none";
        sidenav.style.width = "16%";
        sidenav.style.minWidth = "70px";
        logohead.style.display = "none";
        toggClose.style.fontSize = "0";
        topbar.style.height = "70px";
    add.classList.remove("fa-xmark");
    add.classList.add("fa-bars");

    }
    
}



/*//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////------------------------------------------------To Do List  -----------------------------------------------------
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////*/

// ----------------------------------------global variables-------------------------------------------
var list = [];
var inp = document.getElementById("inp");
var todolist = document.getElementById("todolist");
var editableIndex = null;

// ----------------------------function for adding task by enter_key-----------------------------------
inp.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("btn").click();
    }
})
// ----------------------------------ADD btn click function-------------------------------------------
document.getElementById("btn").addEventListener("click", function () {

    if (inp.value == '') {
        alert("Please enter some title");
        return false;
    }
    else if (editableIndex != null) {
        list.splice(editableIndex, 1, inp.value);
        editableIndex = null;
    }
    else {
        list.push(inp.value)
    }
    document.getElementById("inp").value = "";

    showList()
});
// ----------------------------------------function for list creation-------------------------------------------
function showList() {
    todolist.innerHTML = " "
    list.forEach(function (a, i) {

        todolist.innerHTML += "<br>" +
            "<li>" + "<a>" + a + "</a>" +
            "<div class='btn-host'>" +
            "<button class='edit' onclick='editItem(" + i + ")'> Edit </button>" +
            "<button class='delete' onclick='deleteItem(" + i + ")'>Delete  </button>" +
            "</div>"
        "</li>"
    })
}
// ----------------------------------------function for delete the task-------------------------------------------
function deleteItem(i) {
    list.splice(i, 1)
    showList()
}
// ----------------------------------------function for edit the task-------------------------------------------
function editItem(i) {
    inp.value = list[i];
    editableIndex = i;
}
// ----------------------------------------function for Delete All-------------------------------------------
function clearArray() {
    list = [];
    showList()
}
// ----------------------------------------function for search the task------------------------------------------
function searchTask() {
    var input, filter, ul, li, ai, i, txtValue;


    tosearch = document.getElementById("serinput");
    filter = tosearch.value.toUpperCase();
    ul = document.getElementById("todolist");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        ai = li[i].getElementsByTagName("a")[0];
        txtValue = ai.textContent || ai.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
/*//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
------------------------------------------------Register More Form -----------------------------------------------------
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////*/


